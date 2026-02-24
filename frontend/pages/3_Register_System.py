"""Register a new AI system."""

import streamlit as st

from utils.api_client import api_get, api_post
from utils.constants import (
    BIAS_TESTING_LABELS,
    RISK_TIER_LABELS,
    STATUS_LABELS,
    USE_CASE_LABELS,
    risk_badge,
)

st.set_page_config(page_title="Register System", page_icon="➕", layout="wide")
st.title("Register AI System")

# Fetch categories for descriptions
categories = api_get("/api/classification/categories")
cat_map = {}
if categories:
    cat_map = {c["category"]: c for c in categories}

tab1, tab2, tab3, tab4 = st.tabs(
    ["Basic Info", "Classification", "Governance Details", "Review Schedule"]
)

# Session state for classification result
if "classification_result" not in st.session_state:
    st.session_state.classification_result = None
if "llm_result" not in st.session_state:
    st.session_state.llm_result = None

with tab1:
    name = st.text_input("System Name *", max_chars=255)
    description = st.text_area("Description *", height=100)
    purpose = st.text_area("Purpose & Intended Use *", height=100)
    responsible_team = st.text_input("Responsible Team *", max_chars=255)
    contact_email = st.text_input("Contact Email *", max_chars=255)

    status_options = list(STATUS_LABELS.keys())
    status = st.selectbox(
        "Status",
        status_options,
        format_func=lambda x: STATUS_LABELS[x],
        index=status_options.index("in_development"),
    )

with tab2:
    cat_options = list(USE_CASE_LABELS.keys())
    use_case_category = st.selectbox(
        "Use Case Category *",
        cat_options,
        format_func=lambda x: USE_CASE_LABELS.get(x, x),
    )

    # Show category description
    if use_case_category in cat_map:
        info = cat_map[use_case_category]
        st.caption(info["description"])
        st.caption(f"Examples: {', '.join(info['examples'])}")

    # Rule-based classification
    if st.button("Classify (Rule-Based)"):
        result = api_post(
            "/api/classification/rule-based",
            {"use_case_category": use_case_category},
        )
        if result:
            st.session_state.classification_result = result

    if st.session_state.classification_result:
        r = st.session_state.classification_result
        st.markdown(
            f"**Rule-Based Result:** {risk_badge(r['risk_tier'])}",
            unsafe_allow_html=True,
        )
        st.caption(r["rationale"])

    st.divider()

    # LLM-assisted classification
    st.subheader("AI-Assisted Classification (Optional)")
    llm_desc = st.text_area(
        "Describe the system for AI classification",
        value=description,
        height=80,
        key="llm_description",
    )
    if st.button("Get AI Classification"):
        if len(llm_desc) < 10:
            st.warning("Please provide at least 10 characters.")
        else:
            llm_result = api_post(
                "/api/classification/llm-assisted",
                {
                    "system_description": llm_desc,
                    "purpose": purpose,
                    "data_inputs": None,
                },
            )
            if llm_result:
                st.session_state.llm_result = llm_result

    if st.session_state.llm_result:
        lr = st.session_state.llm_result
        st.markdown(
            f"**AI Suggestion:** {risk_badge(lr['suggested_risk_tier'])} "
            f"(confidence: {lr['confidence']:.0%})",
            unsafe_allow_html=True,
        )
        st.caption(lr["reasoning"])
        if lr.get("relevant_annex_categories"):
            st.caption(
                f"Relevant categories: {', '.join(lr['relevant_annex_categories'])}"
            )

    st.divider()

    # Final tier selection
    tier_options = list(RISK_TIER_LABELS.keys())
    default_idx = 3  # minimal
    if st.session_state.classification_result:
        tier_val = st.session_state.classification_result["risk_tier"]
        if tier_val in tier_options:
            default_idx = tier_options.index(tier_val)

    risk_tier = st.selectbox(
        "Final Risk Tier *",
        tier_options,
        index=default_idx,
        format_func=lambda x: RISK_TIER_LABELS[x],
    )
    risk_rationale = st.text_area("Risk Tier Rationale", height=60)

    # Determine method
    classification_method = "manual"
    if st.session_state.classification_result and risk_tier == st.session_state.classification_result["risk_tier"]:
        classification_method = "rule_based"
    if st.session_state.llm_result and risk_tier == st.session_state.llm_result.get("suggested_risk_tier"):
        classification_method = "llm_assisted"

with tab3:
    data_inputs = st.text_area("Data Inputs", height=80)
    training_data_sources = st.text_area("Training Data Sources", height=80)
    human_oversight = st.text_area("Human Oversight Mechanisms", height=80)

    bias_options = list(BIAS_TESTING_LABELS.keys())
    bias_testing_status = st.selectbox(
        "Bias Testing Status",
        bias_options,
        format_func=lambda x: BIAS_TESTING_LABELS[x],
    )
    bias_testing_results = st.text_area("Bias Testing Results", height=60)
    transparency_measures = st.text_area("Transparency Measures", height=80)

with tab4:
    next_review_date = st.date_input("Next Review Date", value=None)

st.divider()

if st.button("Register System", type="primary"):
    # Validate required fields
    if not name or not description or not purpose or not responsible_team or not contact_email:
        st.error("Please fill in all required fields (marked with *).")
    else:
        payload = {
            "name": name,
            "description": description,
            "purpose": purpose,
            "use_case_category": use_case_category,
            "risk_tier": risk_tier,
            "risk_tier_rationale": risk_rationale or None,
            "risk_classification_method": classification_method,
            "data_inputs": data_inputs or None,
            "training_data_sources": training_data_sources or None,
            "human_oversight": human_oversight or None,
            "bias_testing_status": bias_testing_status,
            "bias_testing_results": bias_testing_results or None,
            "transparency_measures": transparency_measures or None,
            "responsible_team": responsible_team,
            "contact_email": contact_email,
            "status": status,
            "next_review_date": str(next_review_date) if next_review_date else None,
        }
        result = api_post("/api/systems", payload)
        if result:
            st.success(f"System '{result['name']}' registered successfully!")
            st.session_state.classification_result = None
            st.session_state.llm_result = None
            st.query_params["system_id"] = result["id"]
            st.switch_page("pages/7_System_Detail.py")
