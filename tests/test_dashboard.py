"""Tests for dashboard aggregation endpoints."""


def test_summary_empty(client):
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_systems"] == 0
    assert data["high_risk_systems"] == 0
    assert data["overdue_reviews"] == 0


def test_summary_with_data(client, sample_system_data):
    # Create systems of different tiers
    client.post("/api/systems", json=sample_system_data)

    high = dict(sample_system_data)
    high["name"] = "High Risk System"
    high["risk_tier"] = "high"
    high["use_case_category"] = "employment_workers"
    high["status"] = "active"
    client.post("/api/systems", json=high)

    resp = client.get("/api/dashboard/summary")
    data = resp.json()
    assert data["total_systems"] == 2
    assert data["high_risk_systems"] == 1


def test_risk_distribution(client, sample_system_data):
    client.post("/api/systems", json=sample_system_data)

    resp = client.get("/api/dashboard/risk-distribution")
    assert resp.status_code == 200
    data = resp.json()
    assert data["minimal"] == 1
    assert data["high"] == 0


def test_assessment_status(client, created_system):
    client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "A1"},
    )

    resp = client.get("/api/dashboard/assessment-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["draft"] == 1
    assert data["completion_rate"] == 0.0


def test_upcoming_reviews(client, sample_system_data):
    data = dict(sample_system_data)
    data["next_review_date"] = "2099-01-01"
    data["status"] = "active"
    client.post("/api/systems", json=data)

    resp = client.get("/api/dashboard/upcoming-reviews")
    assert resp.status_code == 200
    reviews = resp.json()
    assert len(reviews) == 1
    assert reviews[0]["days_until_review"] > 0


def test_recent_activity(client, created_system):
    resp = client.get("/api/dashboard/recent-activity")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["action"] == "created"
