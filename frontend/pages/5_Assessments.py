"""Impact assessments list page."""

import streamlit as st

from frontend.utils.api_client import api_get, api_post
from frontend.utils.constants import (
    ASSESSMENT_STATUS_COLORS,
    ASSESSMENT_STATUS_LABELS,
    RISK_TIER_LABELS,
    risk_badge,
    status_badge,
)

st.set_page_config(page_title="Assessments", page_icon="📝", layout="wide")
st.title("Impact Assessments")

# Filters
with st.sidebar:
    st.subheader("Filters")
    status_filter = st.selectbox(
        "Status",
        ["All", "draft", "in_review", "approved", "expired"],
        format_func=lambda x: "All" if x == "All" else ASSESSMENT_STATUS_LABELS.get(x, x),
    )

params: dict = {}
if status_filter != "All":
    params["status"] = status_filter

assessments = api_get("/api/assessments", params)

# New assessment section
with st.expander("Create New Assessment"):
    systems = api_get("/api/systems")
    if systems and len(systems) > 0:
        system_options = {s["id"]: s["name"] for s in systems}
        selected_system = st.selectbox(
            "Select AI System",
            list(system_options.keys()),
            format_func=lambda x: system_options[x],
        )
        title = st.text_input("Assessment Title")
        assessor = st.text_input("Assessor Name (optional)")

        if st.button("Create Assessment"):
            if not title:
                st.error("Please provide a title.")
            else:
                result = api_post(
                    "/api/assessments",
                    {
                        "system_id": selected_system,
                        "title": title,
                        "assessor_name": assessor or None,
                    },
                )
                if result:
                    st.success(f"Assessment '{result['title']}' created!")
                    st.query_params["assessment_id"] = result["id"]
                    st.switch_page("frontend/pages/6_Assessment_Detail.py")
    else:
        st.info("Register an AI system first.")

st.divider()

if assessments is None:
    st.stop()

if len(assessments) == 0:
    st.info("No assessments found.")
    st.stop()

st.caption(f"{len(assessments)} assessment(s) found")

for a in assessments:
    with st.container():
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{a['title']}**")
        with cols[1]:
            st.markdown(
                risk_badge(a["risk_tier_at_creation"]),
                unsafe_allow_html=True,
            )
        with cols[2]:
            st.markdown(
                status_badge(
                    a["status"],
                    ASSESSMENT_STATUS_LABELS,
                    ASSESSMENT_STATUS_COLORS,
                ),
                unsafe_allow_html=True,
            )
        with cols[3]:
            if st.button("View", key=f"view_assess_{a['id']}"):
                st.query_params["assessment_id"] = a["id"]
                st.switch_page("frontend/pages/6_Assessment_Detail.py")
    st.divider()
