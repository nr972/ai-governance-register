"""Dashboard — governance posture overview."""

import plotly.express as px
import streamlit as st

from utils.api_client import api_get
from utils.constants import RISK_TIER_COLORS, RISK_TIER_LABELS

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("Governance Dashboard")

# Summary metrics
summary = api_get("/api/dashboard/summary")
if summary:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Systems", summary["total_systems"])
    c2.metric("High Risk", summary["high_risk_systems"])
    c3.metric("Assessments Approved", summary["assessments_approved"])
    c4.metric("Overdue Reviews", summary["overdue_reviews"])

    st.divider()

# Charts row
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Risk Distribution")
    dist = api_get("/api/dashboard/risk-distribution")
    if dist:
        labels = []
        values = []
        colors = []
        for tier in ["unacceptable", "high", "limited", "minimal"]:
            if dist[tier] > 0:
                labels.append(RISK_TIER_LABELS[tier])
                values.append(dist[tier])
                colors.append(RISK_TIER_COLORS[tier])

        if values:
            fig = px.pie(
                names=labels,
                values=values,
                color=labels,
                color_discrete_map=dict(zip(labels, colors)),
                hole=0.4,
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No systems registered yet.")

with col_right:
    st.subheader("Assessment Status")
    assess = api_get("/api/dashboard/assessment-status")
    if assess:
        statuses = ["Draft", "In Review", "Approved", "Expired"]
        counts = [assess["draft"], assess["in_review"], assess["approved"], assess["expired"]]
        bar_colors = ["#9e9e9e", "#1976d2", "#388e3c", "#d32f2f"]

        if any(c > 0 for c in counts):
            fig = px.bar(
                x=statuses,
                y=counts,
                color=statuses,
                color_discrete_map=dict(zip(statuses, bar_colors)),
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                height=300,
                xaxis_title="",
                yaxis_title="Count",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Completion rate: {assess['completion_rate']}%")
        else:
            st.info("No assessments yet.")

st.divider()

# Upcoming reviews
st.subheader("Upcoming Reviews")
reviews = api_get("/api/dashboard/upcoming-reviews")
if reviews:
    if len(reviews) > 0:
        for r in reviews:
            days = r["days_until_review"]
            if days < 7:
                icon = "🔴"
            elif days < 30:
                icon = "🟡"
            else:
                icon = "🟢"
            st.markdown(
                f"{icon} **{r['system_name']}** — "
                f"{r['next_review_date']} ({days} days)"
            )
    else:
        st.info("No upcoming reviews.")
else:
    st.info("No data available.")

# Recent activity
st.divider()
st.subheader("Recent Activity")
activity = api_get("/api/dashboard/recent-activity", {"limit": 10})
if activity:
    for entry in activity:
        action = entry["action"]
        entity = entry["entity_type"].replace("_", " ")
        ts = entry["timestamp"][:16].replace("T", " ")
        st.markdown(f"- `{ts}` — **{action}** {entity}")
else:
    st.info("No recent activity.")
