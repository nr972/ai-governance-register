import enum
import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


# -- Enums -----------------------------------------------------------------


class RiskTier(str, enum.Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"


class SystemStatus(str, enum.Enum):
    ACTIVE = "active"
    IN_DEVELOPMENT = "in_development"
    RETIRED = "retired"
    UNDER_REVIEW = "under_review"


class AssessmentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EXPIRED = "expired"


class BiasTestingStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_APPLICABLE = "not_applicable"


class UseCaseCategory(str, enum.Enum):
    """EU AI Act Annex III high-risk categories plus additional tiers."""

    # Annex III high-risk
    BIOMETRIC_IDENTIFICATION = "biometric_identification"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EDUCATION_VOCATIONAL = "education_vocational"
    EMPLOYMENT_WORKERS = "employment_workers"
    ESSENTIAL_SERVICES = "essential_services"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION_BORDER = "migration_border"
    JUSTICE_DEMOCRACY = "justice_democracy"

    # Limited-risk (transparency obligations)
    CHATBOT_INTERACTION = "chatbot_interaction"
    EMOTION_RECOGNITION = "emotion_recognition"
    DEEPFAKE_GENERATION = "deepfake_generation"

    # Minimal-risk
    CONTENT_RECOMMENDATION = "content_recommendation"
    GENERAL_PURPOSE = "general_purpose"
    OTHER = "other"


# -- Helpers ---------------------------------------------------------------


def _generate_uuid() -> str:
    return str(uuid.uuid4())


# -- Models ----------------------------------------------------------------


class AISystem(Base):
    __tablename__ = "ai_systems"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    use_case_category: Mapped[UseCaseCategory] = mapped_column(
        Enum(UseCaseCategory), nullable=False
    )
    risk_tier: Mapped[RiskTier] = mapped_column(Enum(RiskTier), nullable=False)
    risk_tier_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_classification_method: Mapped[str] = mapped_column(
        String(20), default="rule_based"
    )
    data_inputs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    training_data_sources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    human_oversight: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bias_testing_status: Mapped[BiasTestingStatus] = mapped_column(
        Enum(BiasTestingStatus), default=BiasTestingStatus.NOT_STARTED
    )
    bias_testing_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transparency_measures: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responsible_team: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SystemStatus] = mapped_column(
        Enum(SystemStatus), default=SystemStatus.IN_DEVELOPMENT
    )
    next_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    assessments: Mapped[List["ImpactAssessment"]] = relationship(
        back_populates="ai_system", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="ai_system", cascade="all, delete-orphan"
    )


class ImpactAssessment(Base):
    __tablename__ = "impact_assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    system_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ai_systems.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus), default=AssessmentStatus.DRAFT
    )
    risk_tier_at_creation: Mapped[RiskTier] = mapped_column(
        Enum(RiskTier), nullable=False
    )
    content: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    assessor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    ai_system: Mapped["AISystem"] = relationship(back_populates="assessments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    system_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ai_systems.id"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, index=True
    )

    # Relationships
    ai_system: Mapped["AISystem"] = relationship(back_populates="audit_logs")
