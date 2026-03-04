"""AI Governance Register — Streamlit frontend."""

import streamlit as st

st.set_page_config(
    page_title="AI Governance Register",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
with st.sidebar:
    st.title("AI Governance Register")

    from utils.api_client import api_health

    healthy = api_health()
    if healthy:
        st.success("API Connected", icon="✅")
    else:
        st.error("API Offline", icon="❌")
        st.caption("Start the API: `uvicorn api.main:app --port 8000`")

    st.divider()
    st.caption("[API Docs (Swagger)](http://localhost:8000/docs)")
    st.caption("Built with FastAPI + Streamlit")

# Main content
st.title("AI Governance Register")
st.markdown(
    "Internal AI system registry and governance tracker. "
    "Register AI systems, classify risks under the EU AI Act, "
    "conduct impact assessments, and monitor governance posture."
)

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
    st.caption("View governance posture and risk distribution.")
with col2:
    st.page_link("pages/2_AI_Systems.py", label="AI Systems", icon="🤖")
    st.caption("Browse and manage registered AI systems.")
with col3:
    st.page_link(
        "pages/3_Register_System.py", label="Register System", icon="➕"
    )
    st.caption("Register a new AI system.")

col4, col5, col6 = st.columns(3)
with col4:
    st.page_link(
        "pages/4_Risk_Classification.py",
        label="Risk Classification",
        icon="⚖️",
    )
    st.caption("Classify an AI system's risk tier.")
with col5:
    st.page_link("pages/5_Assessments.py", label="Assessments", icon="📝")
    st.caption("Manage impact assessments.")
with col6:
    # Seed data button
    if st.button("Load Sample Data"):
        from utils.api_client import api_post

        result = api_post("/api/seed", {})
        if result:
            st.success(result.get("message", "Done"))
            st.rerun()
