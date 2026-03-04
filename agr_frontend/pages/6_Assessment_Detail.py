"""Assessment detail — view, fill out, export."""

import requests
import streamlit as st

from utils.api_client import api_get, api_patch, api_put, get_export_url
from utils.constants import (
    ASSESSMENT_STATUS_COLORS,
    ASSESSMENT_STATUS_LABELS,
    risk_badge,
    status_badge,
)

st.set_page_config(page_title="Assessment Detail", page_icon="📝", layout="wide")

assessment_id = st.query_params.get("assessment_id")
if not assessment_id:
    st.warning("No assessment selected. Go to Assessments to pick one.")
    st.page_link("pages/5_Assessments.py", label="Go to Assessments")
    st.stop()

assessment = api_get(f"/api/assessments/{assessment_id}")
if not assessment:
    st.error("Assessment not found.")
    st.stop()

system = api_get(f"/api/systems/{assessment['system_id']}")

# Header
st.title(assessment["title"])
header_cols = st.columns([2, 1, 1, 1])
with header_cols[0]:
    if system:
        st.markdown(f"**System:** {system['name']}")
with header_cols[1]:
    st.markdown(
        f"**Risk Tier:** {risk_badge(assessment['risk_tier_at_creation'])}",
        unsafe_allow_html=True,
    )
with header_cols[2]:
    st.markdown(
        f"**Status:** {status_badge(assessment['status'], ASSESSMENT_STATUS_LABELS, ASSESSMENT_STATUS_COLORS)}",
        unsafe_allow_html=True,
    )
with header_cols[3]:
    if assessment.get("assessor_name"):
        st.caption(f"Assessor: {assessment['assessor_name']}")

# Status actions
st.divider()
action_cols = st.columns(5)
current_status = assessment["status"]

with action_cols[0]:
    if current_status in ("draft", "expired") and st.button("Submit for Review"):
        result = api_patch(
            f"/api/assessments/{assessment_id}/status",
            {"status": "in_review"},
        )
        if result:
            st.rerun()

with action_cols[1]:
    if current_status in ("draft", "in_review"):
        approved_by = st.text_input("Approved by", key="approver", label_visibility="collapsed", placeholder="Approver name")
        if st.button("Approve"):
            if not approved_by:
                st.error("Enter approver name.")
            else:
                result = api_patch(
                    f"/api/assessments/{assessment_id}/status",
                    {"status": "approved", "approved_by": approved_by},
                )
                if result:
                    st.rerun()

with action_cols[2]:
    if current_status == "in_review" and st.button("Back to Draft"):
        result = api_patch(
            f"/api/assessments/{assessment_id}/status",
            {"status": "draft"},
        )
        if result:
            st.rerun()

with action_cols[3]:
    pdf_url = get_export_url(assessment_id, "pdf")
    try:
        pdf_resp = requests.get(pdf_url, timeout=15)
        if pdf_resp.status_code == 200:
            st.download_button(
                "Export PDF",
                data=pdf_resp.content,
                file_name=f"assessment_{assessment_id[:8]}.pdf",
                mime="application/pdf",
            )
    except Exception:
        st.button("Export PDF", disabled=True)

with action_cols[4]:
    docx_url = get_export_url(assessment_id, "docx")
    try:
        docx_resp = requests.get(docx_url, timeout=15)
        if docx_resp.status_code == 200:
            st.download_button(
                "Export DOCX",
                data=docx_resp.content,
                file_name=f"assessment_{assessment_id[:8]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    except Exception:
        st.button("Export DOCX", disabled=True)

st.divider()

# Render assessment sections as editable form
content = assessment.get("content") or {}
sections = content.get("sections", [])

if not sections:
    st.info("This assessment has no content yet.")
    st.stop()

with st.form("assessment_form"):
    updated_sections = []
    for section in sections:
        with st.expander(section["title"], expanded=True):
            if section.get("description"):
                st.caption(section["description"])

            updated_fields = []
            for field in section.get("fields", []):
                fid = f"{section['section_id']}_{field['field_id']}"
                label = field["label"]
                if field.get("required"):
                    label += " *"
                help_text = field.get("help_text", "")
                current_value = field.get("value")
                field_type = field.get("type", "text")

                if field_type == "textarea":
                    new_val = st.text_area(
                        label, value=current_value or "", help=help_text, key=fid
                    )
                elif field_type == "select":
                    options = field.get("options", [])
                    idx = 0
                    if current_value and current_value in options:
                        idx = options.index(current_value)
                    new_val = st.selectbox(
                        label, options, index=idx, help=help_text, key=fid
                    )
                elif field_type == "boolean":
                    new_val = st.checkbox(
                        label,
                        value=bool(current_value),
                        help=help_text,
                        key=fid,
                    )
                elif field_type == "date":
                    new_val = st.text_input(
                        label,
                        value=current_value or "",
                        help=help_text + " (YYYY-MM-DD)",
                        key=fid,
                    )
                else:
                    new_val = st.text_input(
                        label, value=current_value or "", help=help_text, key=fid
                    )

                updated_field = dict(field)
                updated_field["value"] = new_val
                updated_fields.append(updated_field)

            updated_section = dict(section)
            updated_section["fields"] = updated_fields
            updated_sections.append(updated_section)

    if st.form_submit_button("Save Progress", type="primary"):
        updated_content = dict(content)
        updated_content["sections"] = updated_sections
        result = api_put(
            f"/api/assessments/{assessment_id}",
            {"content": updated_content},
        )
        if result:
            st.success("Assessment saved.")
            st.rerun()
