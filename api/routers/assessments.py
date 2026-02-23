from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import (
    AISystem,
    AssessmentStatus,
    ImpactAssessment,
    RiskTier,
)
from api.schemas import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentStatusUpdate,
    AssessmentSummary,
    AssessmentUpdate,
)
from api.services.assessment import generate_assessment_template
from api.services.audit import record_change
from api.services.export import (
    export_assessment_docx,
    export_assessment_pdf,
    get_export_filename,
)

router = APIRouter(prefix="/api/assessments", tags=["Impact Assessments"])


def _get_assessment_or_404(db: Session, assessment_id: str) -> ImpactAssessment:
    assessment = db.get(ImpactAssessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


def _get_system_or_404(db: Session, system_id: str) -> AISystem:
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


# Valid status transitions (flexible: Draft->Approved allowed)
_VALID_TRANSITIONS: dict[AssessmentStatus, set[AssessmentStatus]] = {
    AssessmentStatus.DRAFT: {AssessmentStatus.IN_REVIEW, AssessmentStatus.APPROVED},
    AssessmentStatus.IN_REVIEW: {AssessmentStatus.APPROVED, AssessmentStatus.DRAFT},
    AssessmentStatus.APPROVED: {AssessmentStatus.EXPIRED, AssessmentStatus.IN_REVIEW},
    AssessmentStatus.EXPIRED: {AssessmentStatus.IN_REVIEW, AssessmentStatus.DRAFT},
}


@router.post("", response_model=AssessmentResponse, status_code=201)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    system = _get_system_or_404(db, payload.system_id)

    template = generate_assessment_template(system.risk_tier, system)

    assessment = ImpactAssessment(
        system_id=system.id,
        title=payload.title,
        risk_tier_at_creation=system.risk_tier,
        content=template,
        assessor_name=payload.assessor_name,
    )
    db.add(assessment)
    db.flush()

    record_change(
        db,
        system_id=system.id,
        entity_type="impact_assessment",
        entity_id=assessment.id,
        action="created",
        new_data={
            "title": assessment.title,
            "status": assessment.status,
            "risk_tier_at_creation": assessment.risk_tier_at_creation,
            "assessor_name": assessment.assessor_name,
        },
    )
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("", response_model=list[AssessmentSummary])
def list_assessments(
    system_id: Optional[str] = None,
    status: Optional[AssessmentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(ImpactAssessment)
    if system_id:
        query = query.filter(ImpactAssessment.system_id == system_id)
    if status:
        query = query.filter(ImpactAssessment.status == status)
    query = query.order_by(ImpactAssessment.updated_at.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/templates/{risk_tier}")
def preview_template(risk_tier: RiskTier):
    return generate_assessment_template(risk_tier)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    return _get_assessment_or_404(db, assessment_id)


@router.get("/{assessment_id}/export/pdf")
def export_pdf(assessment_id: str, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    system = _get_system_or_404(db, assessment.system_id)
    buffer = export_assessment_pdf(assessment, system)
    filename = get_export_filename(system, assessment, "pdf")
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{assessment_id}/export/docx")
def export_docx(assessment_id: str, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    system = _get_system_or_404(db, assessment.system_id)
    buffer = export_assessment_docx(assessment, system)
    filename = get_export_filename(system, assessment, "docx")
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.put("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: str,
    payload: AssessmentUpdate,
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    old_data = {
        "title": assessment.title,
        "content": assessment.content,
        "assessor_name": assessment.assessor_name,
    }

    for field, value in update_data.items():
        setattr(assessment, field, value)

    db.flush()
    new_data = {
        "title": assessment.title,
        "content": assessment.content,
        "assessor_name": assessment.assessor_name,
    }

    record_change(
        db,
        system_id=assessment.system_id,
        entity_type="impact_assessment",
        entity_id=assessment.id,
        action="updated",
        old_data=old_data,
        new_data=new_data,
    )
    db.commit()
    db.refresh(assessment)
    return assessment


@router.patch("/{assessment_id}/status", response_model=AssessmentResponse)
def update_assessment_status(
    assessment_id: str,
    payload: AssessmentStatusUpdate,
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)

    valid_next = _VALID_TRANSITIONS.get(assessment.status, set())
    if payload.status not in valid_next:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot transition from '{assessment.status.value}' to "
                f"'{payload.status.value}'. Valid transitions: "
                f"{[s.value for s in valid_next]}"
            ),
        )

    if payload.status == AssessmentStatus.APPROVED and not payload.approved_by:
        raise HTTPException(
            status_code=400,
            detail="'approved_by' is required when approving an assessment.",
        )

    old_status = assessment.status
    assessment.status = payload.status

    if payload.status == AssessmentStatus.APPROVED:
        assessment.approved_by = payload.approved_by
        assessment.approved_at = datetime.now(tz=None)

    db.flush()

    record_change(
        db,
        system_id=assessment.system_id,
        entity_type="impact_assessment",
        entity_id=assessment.id,
        action="updated",
        old_data={"status": old_status},
        new_data={"status": assessment.status},
    )
    db.commit()
    db.refresh(assessment)
    return assessment
