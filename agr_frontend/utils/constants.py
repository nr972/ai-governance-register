"""Display constants for the Streamlit frontend."""

RISK_TIER_COLORS = {
    "unacceptable": "#d32f2f",
    "high": "#f57c00",
    "limited": "#fbc02d",
    "minimal": "#388e3c",
}

RISK_TIER_LABELS = {
    "unacceptable": "Unacceptable",
    "high": "High",
    "limited": "Limited",
    "minimal": "Minimal",
}

STATUS_LABELS = {
    "active": "Active",
    "in_development": "In Development",
    "retired": "Retired",
    "under_review": "Under Review",
}

ASSESSMENT_STATUS_LABELS = {
    "draft": "Draft",
    "in_review": "In Review",
    "approved": "Approved",
    "expired": "Expired",
}

ASSESSMENT_STATUS_COLORS = {
    "draft": "#9e9e9e",
    "in_review": "#1976d2",
    "approved": "#388e3c",
    "expired": "#d32f2f",
}

BIAS_TESTING_LABELS = {
    "not_started": "Not Started",
    "in_progress": "In Progress",
    "completed": "Completed",
    "not_applicable": "Not Applicable",
}

USE_CASE_LABELS = {
    "biometric_identification": "Biometric Identification",
    "critical_infrastructure": "Critical Infrastructure",
    "education_vocational": "Education & Vocational Training",
    "employment_workers": "Employment & Worker Management",
    "essential_services": "Essential Services Access",
    "law_enforcement": "Law Enforcement",
    "migration_border": "Migration & Border Control",
    "justice_democracy": "Justice & Democratic Processes",
    "chatbot_interaction": "Chatbot / Human Interaction",
    "emotion_recognition": "Emotion Recognition",
    "deepfake_generation": "Deepfake / Synthetic Content",
    "content_recommendation": "Content Recommendation",
    "general_purpose": "General Purpose",
    "other": "Other",
}


def risk_badge(tier: str) -> str:
    """Return an HTML badge for a risk tier."""
    color = RISK_TIER_COLORS.get(tier, "#666")
    label = RISK_TIER_LABELS.get(tier, tier)
    return (
        f'<span style="background-color:{color};color:white;padding:2px 8px;'
        f'border-radius:4px;font-size:0.85em;font-weight:600;">{label}</span>'
    )


def status_badge(status: str, labels: dict, colors: dict) -> str:
    """Return an HTML badge for a status value."""
    color = colors.get(status, "#666")
    label = labels.get(status, status)
    return (
        f'<span style="background-color:{color};color:white;padding:2px 8px;'
        f'border-radius:4px;font-size:0.85em;">{label}</span>'
    )
