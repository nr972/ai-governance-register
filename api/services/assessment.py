"""Impact assessment template generation per EU AI Act risk tier."""

from typing import Optional

from api.models import AISystem, RiskTier


def _field(
    field_id: str,
    label: str,
    field_type: str = "text",
    *,
    required: bool = False,
    help_text: str = "",
    options: Optional[list[str]] = None,
    value: Optional[str] = None,
) -> dict:
    f: dict = {
        "field_id": field_id,
        "label": label,
        "type": field_type,
        "required": required,
        "help_text": help_text,
        "value": value,
    }
    if options:
        f["options"] = options
    return f


def _section(
    section_id: str,
    title: str,
    description: str,
    fields: list[dict],
    *,
    required: bool = True,
) -> dict:
    return {
        "section_id": section_id,
        "title": title,
        "description": description,
        "required": required,
        "fields": fields,
    }


# -- Baseline sections (all tiers) ----------------------------------------


def _build_system_overview(system: Optional[AISystem] = None) -> dict:
    return _section(
        "system_overview",
        "System Overview",
        "Basic information about the AI system being assessed.",
        [
            _field(
                "system_name", "System Name", required=True,
                value=system.name if system else None,
            ),
            _field("system_version", "System Version",
                   help_text="Current version or release identifier."),
            _field(
                "assessment_date", "Assessment Date", "date", required=True,
                help_text="Date this assessment is being conducted.",
            ),
            _field("assessor_name", "Assessor Name", required=True,
                   help_text="Person conducting this assessment."),
            _field(
                "system_description", "System Description", "textarea",
                required=True,
                help_text="Detailed description of what the system does.",
                value=system.description if system else None,
            ),
            _field(
                "purpose_and_intended_use", "Purpose & Intended Use", "textarea",
                required=True,
                help_text="Describe the intended use case and target users.",
                value=system.purpose if system else None,
            ),
            _field(
                "deployment_scope", "Deployment Scope", "select", required=True,
                options=["Internal Only", "Customer-Facing", "Both"],
                help_text="Who interacts with or is affected by this system?",
            ),
        ],
    )


def _build_data_practices() -> dict:
    return _section(
        "data_practices",
        "Data Practices",
        "Information about data inputs, storage, and handling.",
        [
            _field("data_sources", "Data Sources", "textarea", required=True,
                   help_text="List all data sources the system ingests."),
            _field("personal_data_involved", "Personal Data Involved?", "boolean",
                   required=True,
                   help_text="Does the system process personal data?"),
            _field("data_retention_period", "Data Retention Period",
                   help_text="How long is input/output data retained?"),
            _field("data_minimization_measures", "Data Minimization Measures",
                   "textarea",
                   help_text="Steps taken to minimize data collection."),
        ],
    )


def _build_risk_assessment() -> dict:
    return _section(
        "risk_assessment",
        "Risk Assessment",
        "Identify and evaluate risks posed by this AI system.",
        [
            _field("identified_risks", "Identified Risks", "textarea",
                   required=True,
                   help_text="List key risks (safety, rights, discrimination, etc.)."),
            _field("risk_mitigation_measures", "Risk Mitigation Measures",
                   "textarea", required=True,
                   help_text="What measures are in place to mitigate each risk?"),
            _field(
                "residual_risk_level", "Residual Risk Level", "select",
                required=True,
                options=["Low", "Medium", "High", "Critical"],
                help_text="Risk level remaining after mitigation.",
            ),
        ],
    )


def _build_human_oversight() -> dict:
    return _section(
        "human_oversight",
        "Human Oversight",
        "Describe mechanisms for human control over the AI system.",
        [
            _field("oversight_mechanism", "Oversight Mechanism", "textarea",
                   required=True,
                   help_text="How can humans monitor and intervene?"),
            _field("escalation_process", "Escalation Process", "textarea",
                   help_text="Process for escalating issues or overriding decisions."),
            _field("human_in_the_loop", "Human-in-the-Loop?", "boolean",
                   required=True,
                   help_text="Does a human review every decision before action?"),
        ],
    )


def _build_review_signoff() -> dict:
    return _section(
        "review_signoff",
        "Review & Sign-off",
        "Final review and approval of this assessment.",
        [
            _field("reviewer_name", "Reviewer Name",
                   help_text="Person reviewing this assessment."),
            _field("review_date", "Review Date", "date"),
            _field("review_notes", "Review Notes", "textarea",
                   help_text="Any notes or conditions from the reviewer."),
            _field("next_review_date", "Next Review Date", "date", required=True,
                   help_text="When should this assessment be revisited?"),
        ],
    )


# -- High-risk extended sections -------------------------------------------


def _build_conformity_assessment() -> dict:
    return _section(
        "conformity_assessment",
        "Conformity Assessment",
        "EU AI Act conformity requirements for high-risk systems.",
        [
            _field(
                "applicable_harmonised_standards",
                "Applicable Harmonised Standards", "textarea", required=True,
                help_text="List relevant harmonised standards (EN, ISO).",
            ),
            _field(
                "technical_documentation_complete",
                "Technical Documentation Complete?", "boolean", required=True,
                help_text="Is technical documentation per Article 11 complete?",
            ),
            _field(
                "quality_management_system",
                "Quality Management System", "textarea", required=True,
                help_text="Describe QMS per Article 17.",
            ),
            _field(
                "eu_declaration_of_conformity",
                "EU Declaration of Conformity Issued?", "boolean",
                help_text="Has a declaration per Article 47 been issued?",
            ),
            _field(
                "notified_body_involvement",
                "Notified Body Involvement", "select",
                options=["Not Required", "Pending", "Completed"],
                help_text="Status of notified body assessment if applicable.",
            ),
        ],
    )


def _build_bias_fairness() -> dict:
    return _section(
        "bias_fairness",
        "Bias & Fairness Testing",
        "Evaluate the system for discriminatory impacts.",
        [
            _field("testing_methodology", "Testing Methodology", "textarea",
                   required=True,
                   help_text="Describe the bias testing approach."),
            _field(
                "protected_characteristics_tested",
                "Protected Characteristics Tested", "textarea", required=True,
                help_text="Which groups were tested (age, gender, ethnicity, etc.)?",
            ),
            _field("test_results_summary", "Test Results Summary", "textarea",
                   required=True,
                   help_text="Summary of bias testing outcomes."),
            _field("disparate_impact_identified", "Disparate Impact Identified?",
                   "boolean", required=True,
                   help_text="Was any disparate impact found?"),
            _field("remediation_actions", "Remediation Actions", "textarea",
                   help_text="Actions taken to address identified disparities."),
        ],
    )


def _build_transparency() -> dict:
    return _section(
        "transparency",
        "Transparency & Explainability",
        "How the system's decisions can be understood and explained.",
        [
            _field("user_notification_mechanism", "User Notification Mechanism",
                   "textarea", required=True,
                   help_text="How are users informed about AI involvement?"),
            _field("explainability_approach", "Explainability Approach", "textarea",
                   required=True,
                   help_text="How can individual decisions be explained?"),
            _field("instructions_for_use", "Instructions for Use Provided?",
                   "boolean", required=True,
                   help_text="Are clear instructions provided per Article 13?"),
            _field("limitations_documented", "Limitations Documented?", "boolean",
                   required=True,
                   help_text="Are known limitations clearly documented?"),
        ],
    )


def _build_robustness_security() -> dict:
    return _section(
        "robustness_security",
        "Robustness & Security",
        "Technical robustness and cybersecurity measures.",
        [
            _field("accuracy_metrics", "Accuracy Metrics", "textarea",
                   required=True,
                   help_text="Key performance and accuracy metrics."),
            _field("cybersecurity_measures", "Cybersecurity Measures", "textarea",
                   required=True,
                   help_text="Security controls protecting the system."),
            _field("adversarial_testing_performed", "Adversarial Testing Performed?",
                   "boolean", required=True,
                   help_text="Has the system been tested against adversarial inputs?"),
            _field("fallback_mechanisms", "Fallback Mechanisms", "textarea",
                   required=True,
                   help_text="What happens when the system fails or is uncertain?"),
        ],
    )


def _build_post_market_monitoring() -> dict:
    return _section(
        "post_market_monitoring",
        "Post-Market Monitoring",
        "Ongoing monitoring after deployment (Article 72).",
        [
            _field("monitoring_plan", "Monitoring Plan", "textarea", required=True,
                   help_text="Describe the post-deployment monitoring approach."),
            _field("incident_reporting_process", "Incident Reporting Process",
                   "textarea", required=True,
                   help_text="Process for reporting serious incidents."),
            _field("performance_metrics_tracked", "Performance Metrics Tracked",
                   "textarea", required=True,
                   help_text="Which metrics are tracked in production?"),
            _field(
                "monitoring_frequency", "Monitoring Frequency", "select",
                required=True,
                options=["Continuous", "Daily", "Weekly", "Monthly", "Quarterly"],
                help_text="How often are monitoring results reviewed?",
            ),
        ],
    )


# -- Limited-risk extended section -----------------------------------------


def _build_transparency_obligations() -> dict:
    return _section(
        "transparency_obligations",
        "Transparency Obligations",
        "Article 52 transparency requirements for limited-risk systems.",
        [
            _field("user_informed_of_ai", "Users Informed of AI?", "boolean",
                   required=True,
                   help_text="Are users clearly told they are interacting with AI?"),
            _field("notification_mechanism", "Notification Mechanism", "textarea",
                   required=True,
                   help_text="How and when are users notified?"),
            _field("deep_fake_disclosure", "Deepfake Disclosure?", "boolean",
                   help_text="If generating synthetic content, is it disclosed?"),
            _field("emotion_recognition_disclosure",
                   "Emotion Recognition Disclosure?", "boolean",
                   help_text="If detecting emotions, is it disclosed?"),
        ],
    )


# -- Public API ------------------------------------------------------------


def generate_assessment_template(
    risk_tier: RiskTier,
    system: Optional[AISystem] = None,
) -> dict:
    """Generate a structured assessment template for the given risk tier.

    Fields from *system* are used to pre-populate known values.
    Returns ``{"sections": [...], "risk_tier": "<tier>"}``.
    """
    sections = [
        _build_system_overview(system),
        _build_data_practices(),
        _build_risk_assessment(),
        _build_human_oversight(),
        _build_review_signoff(),
    ]

    if risk_tier in (RiskTier.HIGH, RiskTier.UNACCEPTABLE):
        sections.extend([
            _build_conformity_assessment(),
            _build_bias_fairness(),
            _build_transparency(),
            _build_robustness_security(),
            _build_post_market_monitoring(),
        ])
    elif risk_tier == RiskTier.LIMITED:
        sections.append(_build_transparency_obligations())

    return {"sections": sections, "risk_tier": risk_tier.value}
