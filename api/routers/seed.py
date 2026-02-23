"""Seed endpoint to load synthetic sample data."""

import json
import os
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import (
    AISystem,
    AssessmentStatus,
    BiasTestingStatus,
    ImpactAssessment,
    RiskTier,
    SystemStatus,
    UseCaseCategory,
)
from api.services.assessment import generate_assessment_template
from api.services.audit import record_change

router = APIRouter(tags=["Seed"])

SEED_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "sample", "seed_data.json"
)


@router.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    """Load synthetic sample data. Idempotent — skips if DB already has data."""
    existing = db.query(AISystem).first()
    if existing:
        return {"message": "Database already contains data. Seed skipped."}

    with open(SEED_FILE) as f:
        data = json.load(f)

    # Map system names to created system objects for assessment linking
    system_map: dict[str, AISystem] = {}

    for raw in data["ai_systems"]:
        system = AISystem(
            name=raw["name"],
            description=raw["description"],
            purpose=raw["purpose"],
            use_case_category=UseCaseCategory(raw["use_case_category"]),
            risk_tier=RiskTier(raw["risk_tier"]),
            risk_tier_rationale=raw.get("risk_tier_rationale"),
            risk_classification_method=raw.get("risk_classification_method", "rule_based"),
            data_inputs=raw.get("data_inputs"),
            training_data_sources=raw.get("training_data_sources"),
            human_oversight=raw.get("human_oversight"),
            bias_testing_status=BiasTestingStatus(raw.get("bias_testing_status", "not_started")),
            bias_testing_results=raw.get("bias_testing_results"),
            transparency_measures=raw.get("transparency_measures"),
            responsible_team=raw["responsible_team"],
            contact_email=raw["contact_email"],
            status=SystemStatus(raw.get("status", "in_development")),
            next_review_date=(
                date.fromisoformat(raw["next_review_date"])
                if raw.get("next_review_date")
                else None
            ),
        )
        db.add(system)
        db.flush()
        system_map[raw["name"]] = system

        record_change(
            db,
            system_id=system.id,
            entity_type="ai_system",
            entity_id=system.id,
            action="created",
            new_data={"name": system.name, "risk_tier": system.risk_tier.value},
        )

    for raw_assess in data["impact_assessments"]:
        system = system_map.get(raw_assess["system_name_ref"])
        if not system:
            continue

        template = generate_assessment_template(system.risk_tier, system)
        status = AssessmentStatus(raw_assess["status"])

        assessment = ImpactAssessment(
            system_id=system.id,
            title=raw_assess["title"],
            status=status,
            risk_tier_at_creation=system.risk_tier,
            content=template,
            assessor_name=raw_assess.get("assessor_name"),
            approved_by=raw_assess.get("approved_by"),
            approved_at=datetime.now(tz=None) if raw_assess.get("approved_by") else None,
        )
        db.add(assessment)
        db.flush()

        record_change(
            db,
            system_id=system.id,
            entity_type="impact_assessment",
            entity_id=assessment.id,
            action="created",
            new_data={"title": assessment.title, "status": status.value},
        )

    db.commit()
    return {
        "message": "Seed data loaded successfully.",
        "systems_created": len(system_map),
        "assessments_created": len(data["impact_assessments"]),
    }
