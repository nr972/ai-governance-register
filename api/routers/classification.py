from fastapi import APIRouter, HTTPException

from api.models import RiskTier
from api.schemas import (
    CategoryInfo,
    ClassificationResponse,
    LLMClassificationRequest,
    LLMClassificationResponse,
    RuleBasedClassificationRequest,
)
from api.services.llm_classifier import classify_with_llm
from api.services.risk_classifier import (
    CATEGORY_INFO,
    CATEGORY_RISK_MAP,
    classify_rule_based,
)

router = APIRouter(prefix="/api/classification", tags=["Risk Classification"])


@router.post("/rule-based", response_model=ClassificationResponse)
def rule_based_classification(payload: RuleBasedClassificationRequest):
    risk_tier, rationale = classify_rule_based(payload.use_case_category)
    return ClassificationResponse(
        risk_tier=risk_tier, rationale=rationale, method="rule_based"
    )


@router.post("/llm-assisted", response_model=LLMClassificationResponse)
async def llm_assisted_classification(payload: LLMClassificationRequest):
    try:
        result = await classify_with_llm(
            system_description=payload.system_description,
            purpose=payload.purpose,
            data_inputs=payload.data_inputs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM classification failed: {exc}",
        )

    return LLMClassificationResponse(
        suggested_risk_tier=RiskTier(result["suggested_risk_tier"]),
        confidence=result["confidence"],
        reasoning=result["reasoning"],
        relevant_annex_categories=result["relevant_annex_categories"],
        method="llm_assisted",
    )


@router.get("/categories", response_model=list[CategoryInfo])
def list_categories():
    categories = []
    for cat, (tier, _rationale) in CATEGORY_RISK_MAP.items():
        info = CATEGORY_INFO[cat]
        categories.append(
            CategoryInfo(
                category=cat,
                display_name=info["display_name"],
                description=info["description"],
                default_risk_tier=tier,
                examples=info["examples"],
            )
        )
    return categories
