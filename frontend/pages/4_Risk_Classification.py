"""Standalone risk classification tool."""

import streamlit as st

from utils.api_client import api_post
from utils.constants import (
    RISK_TIER_COLORS,
    RISK_TIER_LABELS,
    USE_CASE_LABELS,
    risk_badge,
)

st.set_page_config(page_title="Risk Classification", page_icon="⚖️", layout="wide")
st.title("Risk Classification Tool")
st.caption(
    "Classify an AI system's risk tier under the EU AI Act. "
    "No registration required — use this for quick assessments."
)

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rule-Based Classification")
    st.caption("Select a use case category for instant classification.")

    cat_options = list(USE_CASE_LABELS.keys())
    category = st.selectbox(
        "Use Case Category",
        cat_options,
        format_func=lambda x: USE_CASE_LABELS.get(x, x),
        key="rb_category",
    )

    if st.button("Classify", key="rb_btn"):
        result = api_post(
            "/api/classification/rule-based",
            {"use_case_category": category},
        )
        if result:
            tier = result["risk_tier"]
            color = RISK_TIER_COLORS.get(tier, "#666")
            st.markdown("---")
            st.markdown(
                f"### Risk Tier: {risk_badge(tier)}", unsafe_allow_html=True
            )
            st.markdown(f"**Rationale:** {result['rationale']}")

with col_right:
    st.subheader("AI-Assisted Classification")
    st.caption(
        "Provide a free-text description for AI-powered classification. "
        "Requires an Anthropic API key."
    )

    llm_desc = st.text_area(
        "System Description",
        height=120,
        placeholder="Describe the AI system, its purpose, and how it is used...",
        key="llm_desc",
    )
    llm_purpose = st.text_input("Purpose (optional)", key="llm_purpose")
    llm_data = st.text_input("Data Inputs (optional)", key="llm_data")

    if st.button("Get AI Classification", key="llm_btn"):
        if len(llm_desc) < 10:
            st.warning("Please provide at least 10 characters.")
        else:
            result = api_post(
                "/api/classification/llm-assisted",
                {
                    "system_description": llm_desc,
                    "purpose": llm_purpose or None,
                    "data_inputs": llm_data or None,
                },
            )
            if result:
                tier = result["suggested_risk_tier"]
                st.markdown("---")
                st.markdown(
                    f"### Suggested Tier: {risk_badge(tier)}",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Confidence:** {result['confidence']:.0%}")
                st.markdown(f"**Reasoning:** {result['reasoning']}")
                if result.get("relevant_annex_categories"):
                    st.markdown(
                        f"**Relevant categories:** "
                        f"{', '.join(result['relevant_annex_categories'])}"
                    )
