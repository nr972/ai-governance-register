"""Tests for risk classification endpoints."""

import os
from unittest.mock import MagicMock, patch

import pytest

from api.models import RiskTier, UseCaseCategory
from api.services.risk_classifier import CATEGORY_RISK_MAP, classify_rule_based


# -- Rule-based classification (unit) --------------------------------------


@pytest.mark.parametrize("category", list(UseCaseCategory))
def test_every_category_has_mapping(category):
    """Every UseCaseCategory must have a risk mapping."""
    assert category in CATEGORY_RISK_MAP


@pytest.mark.parametrize(
    "category,expected_tier",
    [
        (UseCaseCategory.BIOMETRIC_IDENTIFICATION, RiskTier.HIGH),
        (UseCaseCategory.CRITICAL_INFRASTRUCTURE, RiskTier.HIGH),
        (UseCaseCategory.EMPLOYMENT_WORKERS, RiskTier.HIGH),
        (UseCaseCategory.LAW_ENFORCEMENT, RiskTier.HIGH),
        (UseCaseCategory.CHATBOT_INTERACTION, RiskTier.LIMITED),
        (UseCaseCategory.EMOTION_RECOGNITION, RiskTier.LIMITED),
        (UseCaseCategory.DEEPFAKE_GENERATION, RiskTier.LIMITED),
        (UseCaseCategory.GENERAL_PURPOSE, RiskTier.MINIMAL),
        (UseCaseCategory.CONTENT_RECOMMENDATION, RiskTier.MINIMAL),
        (UseCaseCategory.OTHER, RiskTier.MINIMAL),
    ],
)
def test_rule_based_mapping(category, expected_tier):
    tier, rationale = classify_rule_based(category)
    assert tier == expected_tier
    assert len(rationale) > 0


# -- Rule-based API endpoint -----------------------------------------------


def test_rule_based_endpoint(client):
    resp = client.post(
        "/api/classification/rule-based",
        json={"use_case_category": "employment_workers"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_tier"] == "high"
    assert data["method"] == "rule_based"
    assert len(data["rationale"]) > 0


def test_rule_based_invalid_category(client):
    resp = client.post(
        "/api/classification/rule-based",
        json={"use_case_category": "invalid_category"},
    )
    assert resp.status_code == 422


# -- Categories endpoint ---------------------------------------------------


def test_list_categories(client):
    resp = client.get("/api/classification/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(UseCaseCategory)
    for cat in data:
        assert "category" in cat
        assert "display_name" in cat
        assert "default_risk_tier" in cat
        assert "examples" in cat


# -- LLM-assisted endpoint -------------------------------------------------


def test_llm_endpoint_no_api_key(client):
    with patch.dict(os.environ, {}, clear=False):
        # Ensure no key is set
        os.environ.pop("ANTHROPIC_API_KEY", None)
        resp = client.post(
            "/api/classification/llm-assisted",
            json={"system_description": "A facial recognition system for employee access control."},
        )
        assert resp.status_code == 503


def test_llm_endpoint_short_description(client):
    resp = client.post(
        "/api/classification/llm-assisted",
        json={"system_description": "short"},
    )
    assert resp.status_code == 422


def test_llm_endpoint_success_mocked(client):
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='{"risk_tier":"high","confidence":0.92,"reasoning":"Uses biometric data for identification.","relevant_annex_categories":["biometric_identification"]}'
        )
    ]

    with patch("api.services.llm_classifier.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            resp = client.post(
                "/api/classification/llm-assisted",
                json={
                    "system_description": "A facial recognition system used for building access control with live camera feeds.",
                },
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["suggested_risk_tier"] == "high"
    assert data["confidence"] == 0.92
    assert data["method"] == "llm_assisted"
