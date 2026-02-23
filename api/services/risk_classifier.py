"""Rule-based risk classification aligned to the EU AI Act."""

from api.models import RiskTier, UseCaseCategory

# Mapping derived from EU AI Act Articles 5, 6, and Annex III.
CATEGORY_RISK_MAP: dict[UseCaseCategory, tuple[RiskTier, str]] = {
    # -- High Risk (Annex III) ------------------------------------------------
    UseCaseCategory.BIOMETRIC_IDENTIFICATION: (
        RiskTier.HIGH,
        "Biometric identification systems are classified as high-risk under "
        "EU AI Act Annex III, Category 1. Real-time remote biometric "
        "identification in public spaces for law enforcement is prohibited "
        "(Article 5) with narrow exceptions.",
    ),
    UseCaseCategory.CRITICAL_INFRASTRUCTURE: (
        RiskTier.HIGH,
        "AI systems used as safety components in the management and operation "
        "of critical infrastructure (water, gas, heating, electricity, road "
        "traffic) are high-risk under Annex III, Category 2.",
    ),
    UseCaseCategory.EDUCATION_VOCATIONAL: (
        RiskTier.HIGH,
        "AI systems used to determine access to or assess students in "
        "educational and vocational training institutions are high-risk "
        "under Annex III, Category 3.",
    ),
    UseCaseCategory.EMPLOYMENT_WORKERS: (
        RiskTier.HIGH,
        "AI systems used in recruitment, selection, HR decisions, task "
        "allocation, or monitoring/evaluation of workers are high-risk "
        "under Annex III, Category 4.",
    ),
    UseCaseCategory.ESSENTIAL_SERVICES: (
        RiskTier.HIGH,
        "AI systems used to evaluate creditworthiness, set insurance premiums, "
        "or determine access to essential public/private services are high-risk "
        "under Annex III, Category 5.",
    ),
    UseCaseCategory.LAW_ENFORCEMENT: (
        RiskTier.HIGH,
        "AI systems used by law enforcement for risk assessment, polygraph "
        "alternatives, evidence reliability evaluation, or crime prediction "
        "are high-risk under Annex III, Category 6.",
    ),
    UseCaseCategory.MIGRATION_BORDER: (
        RiskTier.HIGH,
        "AI systems used in migration, asylum, and border control management "
        "are high-risk under Annex III, Category 7.",
    ),
    UseCaseCategory.JUSTICE_DEMOCRACY: (
        RiskTier.HIGH,
        "AI systems used to assist judicial authorities in fact-finding, law "
        "interpretation, or dispute resolution are high-risk under Annex III, "
        "Category 8.",
    ),
    # -- Limited Risk (Article 52 transparency obligations) --------------------
    UseCaseCategory.CHATBOT_INTERACTION: (
        RiskTier.LIMITED,
        "AI systems that interact directly with natural persons (chatbots) are "
        "subject to transparency obligations under Article 52. Users must be "
        "informed they are interacting with an AI system.",
    ),
    UseCaseCategory.EMOTION_RECOGNITION: (
        RiskTier.LIMITED,
        "Emotion recognition systems are subject to transparency obligations "
        "under Article 52. Users must be informed about the operation of the "
        "system.",
    ),
    UseCaseCategory.DEEPFAKE_GENERATION: (
        RiskTier.LIMITED,
        "AI systems that generate or manipulate image, audio, or video content "
        "(deepfakes) are subject to transparency obligations under Article 52.",
    ),
    # -- Minimal Risk ----------------------------------------------------------
    UseCaseCategory.CONTENT_RECOMMENDATION: (
        RiskTier.MINIMAL,
        "Content recommendation and personalization systems generally fall "
        "under minimal risk with no specific regulatory obligations under the "
        "EU AI Act, though voluntary codes of conduct are encouraged.",
    ),
    UseCaseCategory.GENERAL_PURPOSE: (
        RiskTier.MINIMAL,
        "General-purpose AI applications not falling into Annex III categories "
        "are classified as minimal risk. No specific obligations under the "
        "EU AI Act, though voluntary codes of conduct apply.",
    ),
    UseCaseCategory.OTHER: (
        RiskTier.MINIMAL,
        "Use cases not specifically enumerated in the EU AI Act are "
        "provisionally classified as minimal risk. Review the specific "
        "application against Annex III categories to confirm.",
    ),
}

# Category metadata for the /categories endpoint
CATEGORY_INFO: dict[UseCaseCategory, dict] = {
    UseCaseCategory.BIOMETRIC_IDENTIFICATION: {
        "display_name": "Biometric Identification",
        "description": "Systems that identify individuals based on biometric data (facial recognition, fingerprints, voice).",
        "examples": [
            "Facial recognition for building access",
            "Voice authentication for call centers",
            "Fingerprint matching for identity verification",
        ],
    },
    UseCaseCategory.CRITICAL_INFRASTRUCTURE: {
        "display_name": "Critical Infrastructure",
        "description": "AI used as safety components in management of critical infrastructure.",
        "examples": [
            "Power grid demand forecasting",
            "Water treatment monitoring",
            "Traffic management systems",
        ],
    },
    UseCaseCategory.EDUCATION_VOCATIONAL: {
        "display_name": "Education & Vocational Training",
        "description": "AI used to determine access to education or assess students.",
        "examples": [
            "Automated essay grading",
            "Student admission scoring",
            "Learning path personalization that affects grades",
        ],
    },
    UseCaseCategory.EMPLOYMENT_WORKERS: {
        "display_name": "Employment & Worker Management",
        "description": "AI used in recruitment, HR decisions, task allocation, or worker monitoring.",
        "examples": [
            "Resume screening and candidate ranking",
            "Automated interview assessment",
            "Employee performance monitoring",
        ],
    },
    UseCaseCategory.ESSENTIAL_SERVICES: {
        "display_name": "Essential Services Access",
        "description": "AI used to evaluate creditworthiness, set insurance premiums, or control access to essential services.",
        "examples": [
            "Credit scoring models",
            "Insurance risk pricing",
            "Benefits eligibility determination",
        ],
    },
    UseCaseCategory.LAW_ENFORCEMENT: {
        "display_name": "Law Enforcement",
        "description": "AI used by law enforcement for risk assessment, evidence evaluation, or crime prediction.",
        "examples": [
            "Predictive policing",
            "Risk assessment for bail/sentencing",
            "Evidence analysis tools",
        ],
    },
    UseCaseCategory.MIGRATION_BORDER: {
        "display_name": "Migration & Border Control",
        "description": "AI used in migration, asylum, and border control management.",
        "examples": [
            "Asylum application assessment",
            "Border surveillance systems",
            "Travel document verification",
        ],
    },
    UseCaseCategory.JUSTICE_DEMOCRACY: {
        "display_name": "Justice & Democratic Processes",
        "description": "AI used to assist judicial authorities or influence democratic processes.",
        "examples": [
            "Legal research assistants for judges",
            "Sentencing recommendation systems",
            "Election-related content moderation",
        ],
    },
    UseCaseCategory.CHATBOT_INTERACTION: {
        "display_name": "Chatbot / Human Interaction",
        "description": "AI systems that interact directly with people in conversational interfaces.",
        "examples": [
            "Customer support chatbots",
            "Virtual assistants",
            "Conversational AI interfaces",
        ],
    },
    UseCaseCategory.EMOTION_RECOGNITION: {
        "display_name": "Emotion Recognition",
        "description": "Systems that detect or infer emotions from biometric or behavioral signals.",
        "examples": [
            "Sentiment analysis from facial expressions",
            "Voice-based emotion detection",
            "Employee mood monitoring",
        ],
    },
    UseCaseCategory.DEEPFAKE_GENERATION: {
        "display_name": "Deepfake / Synthetic Content",
        "description": "AI that generates or manipulates image, audio, or video content.",
        "examples": [
            "AI-generated video content",
            "Voice cloning",
            "Synthetic image generation",
        ],
    },
    UseCaseCategory.CONTENT_RECOMMENDATION: {
        "display_name": "Content Recommendation",
        "description": "Systems that recommend or personalize content for users.",
        "examples": [
            "Article recommendation engines",
            "Product suggestion algorithms",
            "Content feed personalization",
        ],
    },
    UseCaseCategory.GENERAL_PURPOSE: {
        "display_name": "General Purpose",
        "description": "General-purpose AI not falling into a specific Annex III category.",
        "examples": [
            "Document OCR and digitization",
            "Internal search optimization",
            "Workflow automation",
        ],
    },
    UseCaseCategory.OTHER: {
        "display_name": "Other",
        "description": "Use cases not covered by the categories above. Review against Annex III manually.",
        "examples": [
            "Custom internal tools",
            "Experimental AI projects",
            "Research prototypes",
        ],
    },
}


def classify_rule_based(category: UseCaseCategory) -> tuple[RiskTier, str]:
    """Return (risk_tier, rationale) for a given use-case category."""
    return CATEGORY_RISK_MAP[category]
