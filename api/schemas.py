from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from api.models import (
    AssessmentStatus,
    BiasTestingStatus,
    RiskTier,
    SystemStatus,
    UseCaseCategory,
)


# -- AI System Schemas -----------------------------------------------------


class AISystemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    purpose: str = Field(..., min_length=1)
    use_case_category: UseCaseCategory
    risk_tier: RiskTier
    risk_tier_rationale: Optional[str] = None
    risk_classification_method: str = Field(default="rule_based", max_length=20)
    data_inputs: Optional[str] = None
    training_data_sources: Optional[str] = None
    human_oversight: Optional[str] = None
    bias_testing_status: BiasTestingStatus = BiasTestingStatus.NOT_STARTED
    bias_testing_results: Optional[str] = None
    transparency_measures: Optional[str] = None
    responsible_team: str = Field(..., min_length=1, max_length=255)
    contact_email: str = Field(..., min_length=1, max_length=255)
    status: SystemStatus = SystemStatus.IN_DEVELOPMENT
    next_review_date: Optional[date] = None


class AISystemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    purpose: Optional[str] = Field(None, min_length=1)
    use_case_category: Optional[UseCaseCategory] = None
    risk_tier: Optional[RiskTier] = None
    risk_tier_rationale: Optional[str] = None
    risk_classification_method: Optional[str] = Field(None, max_length=20)
    data_inputs: Optional[str] = None
    training_data_sources: Optional[str] = None
    human_oversight: Optional[str] = None
    bias_testing_status: Optional[BiasTestingStatus] = None
    bias_testing_results: Optional[str] = None
    transparency_measures: Optional[str] = None
    responsible_team: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[SystemStatus] = None
    next_review_date: Optional[date] = None


class AISystemResponse(BaseModel):
    id: str
    name: str
    description: str
    purpose: str
    use_case_category: UseCaseCategory
    risk_tier: RiskTier
    risk_tier_rationale: Optional[str]
    risk_classification_method: str
    data_inputs: Optional[str]
    training_data_sources: Optional[str]
    human_oversight: Optional[str]
    bias_testing_status: BiasTestingStatus
    bias_testing_results: Optional[str]
    transparency_measures: Optional[str]
    responsible_team: str
    contact_email: str
    status: SystemStatus
    next_review_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AISystemSummary(BaseModel):
    id: str
    name: str
    risk_tier: RiskTier
    status: SystemStatus
    responsible_team: str
    next_review_date: Optional[date]
    updated_at: datetime

    model_config = {"from_attributes": True}


# -- Classification Schemas ------------------------------------------------


class RuleBasedClassificationRequest(BaseModel):
    use_case_category: UseCaseCategory


class ClassificationResponse(BaseModel):
    risk_tier: RiskTier
    rationale: str
    method: str = "rule_based"


class LLMClassificationRequest(BaseModel):
    system_description: str = Field(..., min_length=10, max_length=5000)
    purpose: Optional[str] = None
    data_inputs: Optional[str] = None


class LLMClassificationResponse(BaseModel):
    suggested_risk_tier: RiskTier
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    relevant_annex_categories: List[str]
    method: str = "llm_assisted"


class CategoryInfo(BaseModel):
    category: UseCaseCategory
    display_name: str
    description: str
    default_risk_tier: RiskTier
    examples: List[str]


# -- Assessment Schemas ----------------------------------------------------


class AssessmentCreate(BaseModel):
    system_id: str
    title: str = Field(..., min_length=1, max_length=255)
    assessor_name: Optional[str] = None


class AssessmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[dict] = None
    assessor_name: Optional[str] = None


class AssessmentStatusUpdate(BaseModel):
    status: AssessmentStatus
    approved_by: Optional[str] = None


class AssessmentResponse(BaseModel):
    id: str
    system_id: str
    title: str
    status: AssessmentStatus
    risk_tier_at_creation: RiskTier
    content: Optional[dict]
    assessor_name: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    expires_at: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssessmentSummary(BaseModel):
    id: str
    system_id: str
    title: str
    status: AssessmentStatus
    risk_tier_at_creation: RiskTier
    assessor_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# -- Dashboard Schemas -----------------------------------------------------


class DashboardSummary(BaseModel):
    total_systems: int
    active_systems: int
    systems_under_review: int
    total_assessments: int
    assessments_approved: int
    assessments_expired: int
    high_risk_systems: int
    overdue_reviews: int


class RiskDistribution(BaseModel):
    unacceptable: int
    high: int
    limited: int
    minimal: int


class AssessmentStatusSummary(BaseModel):
    draft: int
    in_review: int
    approved: int
    expired: int
    completion_rate: float


class UpcomingReview(BaseModel):
    system_id: str
    system_name: str
    risk_tier: RiskTier
    next_review_date: date
    days_until_review: int

    model_config = {"from_attributes": True}


# -- Audit Log Schemas -----------------------------------------------------


class AuditLogResponse(BaseModel):
    id: str
    system_id: str
    entity_type: str
    entity_id: str
    action: str
    changes: Optional[dict]
    timestamp: datetime

    model_config = {"from_attributes": True}
