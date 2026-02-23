from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import AISystem, AuditLog, RiskTier, SystemStatus
from api.schemas import (
    AISystemCreate,
    AISystemResponse,
    AISystemSummary,
    AISystemUpdate,
    AuditLogResponse,
)
from api.services.audit import record_change

router = APIRouter(prefix="/api/systems", tags=["AI Systems"])


def _system_to_dict(system: AISystem) -> dict:
    """Extract model fields as a plain dict for audit diffing."""
    return {
        "name": system.name,
        "description": system.description,
        "purpose": system.purpose,
        "use_case_category": system.use_case_category,
        "risk_tier": system.risk_tier,
        "risk_tier_rationale": system.risk_tier_rationale,
        "risk_classification_method": system.risk_classification_method,
        "data_inputs": system.data_inputs,
        "training_data_sources": system.training_data_sources,
        "human_oversight": system.human_oversight,
        "bias_testing_status": system.bias_testing_status,
        "bias_testing_results": system.bias_testing_results,
        "transparency_measures": system.transparency_measures,
        "responsible_team": system.responsible_team,
        "contact_email": system.contact_email,
        "status": system.status,
        "next_review_date": system.next_review_date,
    }


def _get_system_or_404(db: Session, system_id: str) -> AISystem:
    system = db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


@router.post("", response_model=AISystemResponse, status_code=201)
def create_system(payload: AISystemCreate, db: Session = Depends(get_db)):
    system = AISystem(**payload.model_dump())
    db.add(system)
    db.flush()

    record_change(
        db,
        system_id=system.id,
        entity_type="ai_system",
        entity_id=system.id,
        action="created",
        new_data=_system_to_dict(system),
    )
    db.commit()
    db.refresh(system)
    return system


@router.get("", response_model=list[AISystemSummary])
def list_systems(
    status: Optional[SystemStatus] = None,
    risk_tier: Optional[RiskTier] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(AISystem)
    if status:
        query = query.filter(AISystem.status == status)
    if risk_tier:
        query = query.filter(AISystem.risk_tier == risk_tier)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                AISystem.name.ilike(pattern),
                AISystem.description.ilike(pattern),
                AISystem.responsible_team.ilike(pattern),
            )
        )
    query = query.order_by(AISystem.updated_at.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/{system_id}", response_model=AISystemResponse)
def get_system(system_id: str, db: Session = Depends(get_db)):
    return _get_system_or_404(db, system_id)


@router.put("/{system_id}", response_model=AISystemResponse)
def update_system(
    system_id: str, payload: AISystemUpdate, db: Session = Depends(get_db)
):
    system = _get_system_or_404(db, system_id)
    old_data = _system_to_dict(system)

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(system, field, value)

    db.flush()
    new_data = _system_to_dict(system)

    record_change(
        db,
        system_id=system.id,
        entity_type="ai_system",
        entity_id=system.id,
        action="updated",
        old_data=old_data,
        new_data=new_data,
    )
    db.commit()
    db.refresh(system)
    return system


@router.delete("/{system_id}", status_code=204)
def delete_system(system_id: str, db: Session = Depends(get_db)):
    system = _get_system_or_404(db, system_id)
    old_data = _system_to_dict(system)

    record_change(
        db,
        system_id=system.id,
        entity_type="ai_system",
        entity_id=system.id,
        action="deleted",
        old_data=old_data,
    )
    db.delete(system)
    db.commit()


@router.get("/{system_id}/history", response_model=list[AuditLogResponse])
def get_system_history(
    system_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    _get_system_or_404(db, system_id)
    return (
        db.query(AuditLog)
        .filter(AuditLog.system_id == system_id)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
