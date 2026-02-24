"""AI Systems list page."""

import streamlit as st

from utils.api_client import api_get
from utils.constants import (
    RISK_TIER_LABELS,
    STATUS_LABELS,
    risk_badge,
)

st.set_page_config(page_title="AI Systems", page_icon="🤖", layout="wide")
st.title("AI Systems Registry")

# Filters
with st.sidebar:
    st.subheader("Filters")
    risk_filter = st.selectbox(
        "Risk Tier",
        ["All", "unacceptable", "high", "limited", "minimal"],
        format_func=lambda x: "All" if x == "All" else RISK_TIER_LABELS.get(x, x),
    )
    status_filter = st.selectbox(
        "Status",
        ["All", "active", "in_development", "retired", "under_review"],
        format_func=lambda x: "All" if x == "All" else STATUS_LABELS.get(x, x),
    )
    search = st.text_input("Search", placeholder="System name, team...")

# Build query params
params: dict = {}
if risk_filter != "All":
    params["risk_tier"] = risk_filter
if status_filter != "All":
    params["status"] = status_filter
if search:
    params["search"] = search

systems = api_get("/api/systems", params)

if systems is None:
    st.stop()

if len(systems) == 0:
    st.info("No AI systems found. Register one or load sample data.")
    st.page_link("pages/3_Register_System.py", label="Register New System", icon="➕")
    st.stop()

st.caption(f"{len(systems)} system(s) found")

for s in systems:
    with st.container():
        cols = st.columns([3, 1, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{s['name']}**")
        with cols[1]:
            st.markdown(risk_badge(s["risk_tier"]), unsafe_allow_html=True)
        with cols[2]:
            st.caption(STATUS_LABELS.get(s["status"], s["status"]))
        with cols[3]:
            st.caption(s["responsible_team"])
        with cols[4]:
            if st.button("View", key=f"view_{s['id']}"):
                st.query_params["system_id"] = s["id"]
                st.switch_page("pages/7_System_Detail.py")
    st.divider()
