"""System detail — view, edit, history."""

import streamlit as st

from utils.api_client import api_delete, api_get, api_put
from utils.constants import (
    ASSESSMENT_STATUS_COLORS,
    ASSESSMENT_STATUS_LABELS,
    BIAS_TESTING_LABELS,
    RISK_TIER_LABELS,
    STATUS_LABELS,
    USE_CASE_LABELS,
    risk_badge,
    status_badge,
)

st.set_page_config(page_title="System Detail", page_icon="🤖", layout="wide")

system_id = st.query_params.get("system_id")
if not system_id:
    st.warning("No system selected. Go to AI Systems to pick one.")
    st.page_link("pages/2_AI_Systems.py", label="Go to AI Systems")
    st.stop()

system = api_get(f"/api/systems/{system_id}")
if not system:
    st.error("System not found.")
    st.stop()

# Header
st.title(system["name"])
hcols = st.columns([1, 1, 1])
with hcols[0]:
    st.markdown(risk_badge(system["risk_tier"]), unsafe_allow_html=True)
with hcols[1]:
    st.caption(f"Status: {STATUS_LABELS.get(system['status'], system['status'])}")
with hcols[2]:
    st.caption(f"Team: {system['responsible_team']}")

tab_overview, tab_assessments, tab_history, tab_edit = st.tabs(
    ["Overview", "Assessments", "History", "Edit"]
)

# -- Overview tab -----------------------------------------------------------
with tab_overview:
    st.subheader("System Information")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Description:** {system['description']}")
        st.markdown(f"**Purpose:** {system['purpose']}")
        st.markdown(
            f"**Use Case Category:** "
            f"{USE_CASE_LABELS.get(system['use_case_category'], system['use_case_category'])}"
        )
        st.markdown(f"**Classification Method:** {system['risk_classification_method']}")
        if system.get("risk_tier_rationale"):
            st.markdown(f"**Risk Rationale:** {system['risk_tier_rationale']}")

    with col2:
        st.markdown(f"**Data Inputs:** {system.get('data_inputs') or 'N/A'}")
        st.markdown(
            f"**Training Data Sources:** {system.get('training_data_sources') or 'N/A'}"
        )
        st.markdown(
            f"**Human Oversight:** {system.get('human_oversight') or 'N/A'}"
        )
        st.markdown(
            f"**Bias Testing:** "
            f"{BIAS_TESTING_LABELS.get(system['bias_testing_status'], system['bias_testing_status'])}"
        )
        if system.get("bias_testing_results"):
            st.markdown(f"**Bias Results:** {system['bias_testing_results']}")
        st.markdown(
            f"**Transparency:** {system.get('transparency_measures') or 'N/A'}"
        )

    st.divider()
    st.markdown(f"**Contact:** {system['contact_email']}")
    if system.get("next_review_date"):
        st.markdown(f"**Next Review:** {system['next_review_date']}")
    st.caption(f"Created: {system['created_at'][:16]} | Updated: {system['updated_at'][:16]}")

# -- Assessments tab --------------------------------------------------------
with tab_assessments:
    assessments = api_get("/api/assessments", {"system_id": system_id})
    if assessments and len(assessments) > 0:
        for a in assessments:
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.markdown(f"**{a['title']}**")
            with cols[1]:
                st.markdown(
                    status_badge(
                        a["status"],
                        ASSESSMENT_STATUS_LABELS,
                        ASSESSMENT_STATUS_COLORS,
                    ),
                    unsafe_allow_html=True,
                )
            with cols[2]:
                if st.button("View", key=f"assess_{a['id']}"):
                    st.query_params["assessment_id"] = a["id"]
                    st.switch_page("pages/6_Assessment_Detail.py")
            st.divider()
    else:
        st.info("No assessments for this system yet.")

    if st.button("Create Assessment for This System"):
        st.query_params["system_id"] = system_id
        st.switch_page("pages/5_Assessments.py")

# -- History tab ------------------------------------------------------------
with tab_history:
    history = api_get(f"/api/systems/{system_id}/history")
    if history and len(history) > 0:
        for entry in history:
            ts = entry["timestamp"][:16].replace("T", " ")
            action = entry["action"]
            entity = entry["entity_type"].replace("_", " ")

            st.markdown(f"**{ts}** — {action} {entity}")
            changes = entry.get("changes", {})
            if changes:
                for field, diff in changes.items():
                    old_val = diff.get("old", "—")
                    new_val = diff.get("new", "—")
                    if old_val is None:
                        old_val = "—"
                    if new_val is None:
                        new_val = "—"
                    st.caption(f"  {field}: {old_val} → {new_val}")
            st.divider()
    else:
        st.info("No history available.")

# -- Edit tab ---------------------------------------------------------------
with tab_edit:
    with st.form("edit_system"):
        edit_name = st.text_input("System Name", value=system["name"])
        edit_desc = st.text_area("Description", value=system["description"])
        edit_purpose = st.text_area("Purpose", value=system["purpose"])

        tier_opts = list(RISK_TIER_LABELS.keys())
        edit_tier = st.selectbox(
            "Risk Tier",
            tier_opts,
            index=tier_opts.index(system["risk_tier"]),
            format_func=lambda x: RISK_TIER_LABELS[x],
        )

        status_opts = list(STATUS_LABELS.keys())
        edit_status = st.selectbox(
            "Status",
            status_opts,
            index=status_opts.index(system["status"]),
            format_func=lambda x: STATUS_LABELS[x],
        )

        edit_team = st.text_input(
            "Responsible Team", value=system["responsible_team"]
        )
        edit_email = st.text_input(
            "Contact Email", value=system["contact_email"]
        )
        edit_oversight = st.text_area(
            "Human Oversight",
            value=system.get("human_oversight") or "",
        )
        edit_transparency = st.text_area(
            "Transparency Measures",
            value=system.get("transparency_measures") or "",
        )

        if st.form_submit_button("Save Changes", type="primary"):
            payload = {
                "name": edit_name,
                "description": edit_desc,
                "purpose": edit_purpose,
                "risk_tier": edit_tier,
                "status": edit_status,
                "responsible_team": edit_team,
                "contact_email": edit_email,
                "human_oversight": edit_oversight or None,
                "transparency_measures": edit_transparency or None,
            }
            result = api_put(f"/api/systems/{system_id}", payload)
            if result:
                st.success("System updated.")
                st.rerun()

    st.divider()
    st.subheader("Danger Zone")
    if st.button("Delete System", type="secondary"):
        st.warning("This will permanently delete the system and all its assessments.")
        if st.button("Confirm Delete", type="primary", key="confirm_delete"):
            if api_delete(f"/api/systems/{system_id}"):
                st.success("System deleted.")
                st.switch_page("pages/2_AI_Systems.py")
