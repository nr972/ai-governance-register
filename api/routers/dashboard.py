from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import (
    AISystem,
    AssessmentStatus,
    AuditLog,
    ImpactAssessment,
    RiskTier,
    SystemStatus,
)
from api.schemas import (
    AssessmentStatusSummary,
    AuditLogResponse,
    DashboardSummary,
    RiskDistribution,
    UpcomingReview,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    today = date.today()

    total_systems = db.query(func.count(AISystem.id)).scalar() or 0
    active_systems = (
        db.query(func.count(AISystem.id))
        .filter(AISystem.status == SystemStatus.ACTIVE)
        .scalar() or 0
    )
    systems_under_review = (
        db.query(func.count(AISystem.id))
        .filter(AISystem.status == SystemStatus.UNDER_REVIEW)
        .scalar() or 0
    )
    total_assessments = (
        db.query(func.count(ImpactAssessment.id)).scalar() or 0
    )
    assessments_approved = (
        db.query(func.count(ImpactAssessment.id))
        .filter(ImpactAssessment.status == AssessmentStatus.APPROVED)
        .scalar() or 0
    )
    assessments_expired = (
        db.query(func.count(ImpactAssessment.id))
        .filter(ImpactAssessment.status == AssessmentStatus.EXPIRED)
        .scalar() or 0
    )
    high_risk_systems = (
        db.query(func.count(AISystem.id))
        .filter(AISystem.risk_tier.in_([RiskTier.HIGH, RiskTier.UNACCEPTABLE]))
        .scalar() or 0
    )
    overdue_reviews = (
        db.query(func.count(AISystem.id))
        .filter(
            AISystem.next_review_date.isnot(None),
            AISystem.next_review_date < today,
            AISystem.status != SystemStatus.RETIRED,
        )
        .scalar() or 0
    )

    return DashboardSummary(
        total_systems=total_systems,
        active_systems=active_systems,
        systems_under_review=systems_under_review,
        total_assessments=total_assessments,
        assessments_approved=assessments_approved,
        assessments_expired=assessments_expired,
        high_risk_systems=high_risk_systems,
        overdue_reviews=overdue_reviews,
    )


@router.get("/risk-distribution", response_model=RiskDistribution)
def get_risk_distribution(db: Session = Depends(get_db)):
    counts = {tier: 0 for tier in RiskTier}
    rows = (
        db.query(AISystem.risk_tier, func.count(AISystem.id))
        .group_by(AISystem.risk_tier)
        .all()
    )
    for tier, count in rows:
        counts[tier] = count

    return RiskDistribution(
        unacceptable=counts[RiskTier.UNACCEPTABLE],
        high=counts[RiskTier.HIGH],
        limited=counts[RiskTier.LIMITED],
        minimal=counts[RiskTier.MINIMAL],
    )


@router.get("/assessment-status", response_model=AssessmentStatusSummary)
def get_assessment_status(db: Session = Depends(get_db)):
    counts = {s: 0 for s in AssessmentStatus}
    rows = (
        db.query(ImpactAssessment.status, func.count(ImpactAssessment.id))
        .group_by(ImpactAssessment.status)
        .all()
    )
    for status, count in rows:
        counts[status] = count

    total = sum(counts.values())
    approved = counts[AssessmentStatus.APPROVED]
    rate = (approved / total * 100) if total > 0 else 0.0

    return AssessmentStatusSummary(
        draft=counts[AssessmentStatus.DRAFT],
        in_review=counts[AssessmentStatus.IN_REVIEW],
        approved=approved,
        expired=counts[AssessmentStatus.EXPIRED],
        completion_rate=round(rate, 1),
    )


@router.get("/upcoming-reviews", response_model=list[UpcomingReview])
def get_upcoming_reviews(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    today = date.today()
    systems = (
        db.query(AISystem)
        .filter(
            AISystem.next_review_date.isnot(None),
            AISystem.next_review_date >= today,
            AISystem.status != SystemStatus.RETIRED,
        )
        .order_by(AISystem.next_review_date.asc())
        .limit(limit)
        .all()
    )

    return [
        UpcomingReview(
            system_id=s.id,
            system_name=s.name,
            risk_tier=s.risk_tier,
            next_review_date=s.next_review_date,
            days_until_review=(s.next_review_date - today).days,
        )
        for s in systems
    ]


@router.get("/recent-activity", response_model=list[AuditLogResponse])
def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )
