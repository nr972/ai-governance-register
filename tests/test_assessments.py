"""Tests for impact assessment endpoints."""


def test_create_assessment(client, created_system):
    resp = client.post(
        "/api/assessments",
        json={
            "system_id": created_system["id"],
            "title": "Test Assessment",
            "assessor_name": "Tester",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Assessment"
    assert data["status"] == "draft"
    assert data["risk_tier_at_creation"] == created_system["risk_tier"]
    assert data["content"] is not None
    assert "sections" in data["content"]


def test_create_assessment_system_not_found(client):
    resp = client.post(
        "/api/assessments",
        json={"system_id": "nonexistent", "title": "Test"},
    )
    assert resp.status_code == 404


def test_assessment_template_minimal(client, created_system):
    """Minimal-risk system gets 5 baseline sections."""
    resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "Minimal Test"},
    )
    data = resp.json()
    sections = data["content"]["sections"]
    assert len(sections) == 5


def test_assessment_template_high_risk(client, sample_system_data):
    """High-risk system gets 10 sections (5 baseline + 5 extended)."""
    high_data = dict(sample_system_data)
    high_data["risk_tier"] = "high"
    high_data["use_case_category"] = "employment_workers"
    system = client.post("/api/systems", json=high_data).json()

    resp = client.post(
        "/api/assessments",
        json={"system_id": system["id"], "title": "High Risk Test"},
    )
    data = resp.json()
    sections = data["content"]["sections"]
    assert len(sections) == 10


def test_assessment_template_limited_risk(client, sample_system_data):
    """Limited-risk system gets 6 sections (5 baseline + 1 transparency)."""
    limited_data = dict(sample_system_data)
    limited_data["risk_tier"] = "limited"
    limited_data["use_case_category"] = "chatbot_interaction"
    system = client.post("/api/systems", json=limited_data).json()

    resp = client.post(
        "/api/assessments",
        json={"system_id": system["id"], "title": "Limited Risk Test"},
    )
    data = resp.json()
    sections = data["content"]["sections"]
    assert len(sections) == 6


def test_list_assessments(client, created_system):
    client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "A1"},
    )
    resp = client.get("/api/assessments")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_assessments_filter_system(client, created_system, sample_system_data):
    # Create two systems with assessments
    client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "A1"},
    )

    other = dict(sample_system_data)
    other["name"] = "Other System"
    other_system = client.post("/api/systems", json=other).json()
    client.post(
        "/api/assessments",
        json={"system_id": other_system["id"], "title": "A2"},
    )

    resp = client.get(
        "/api/assessments", params={"system_id": created_system["id"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "A1"


def test_get_assessment(client, created_system):
    create_resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "Detail Test"},
    )
    aid = create_resp.json()["id"]
    resp = client.get(f"/api/assessments/{aid}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Detail Test"


def test_get_assessment_not_found(client):
    resp = client.get("/api/assessments/nonexistent")
    assert resp.status_code == 404


def test_update_assessment(client, created_system):
    create_resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "Update Test"},
    )
    aid = create_resp.json()["id"]

    resp = client.put(
        f"/api/assessments/{aid}",
        json={"title": "Updated Title"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


def test_status_draft_to_in_review(client, created_system):
    create_resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "Status Test"},
    )
    aid = create_resp.json()["id"]

    resp = client.patch(
        f"/api/assessments/{aid}/status",
        json={"status": "in_review"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_review"


def test_status_draft_to_approved_flexible(client, created_system):
    """Flexible workflow: Draft -> Approved directly."""
    create_resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "Direct Approve"},
    )
    aid = create_resp.json()["id"]

    resp = client.patch(
        f"/api/assessments/{aid}/status",
        json={"status": "approved", "approved_by": "Admin"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
    assert resp.json()["approved_by"] == "Admin"


def test_status_approved_requires_approver(client, created_system):
    create_resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "No Approver"},
    )
    aid = create_resp.json()["id"]

    resp = client.patch(
        f"/api/assessments/{aid}/status",
        json={"status": "approved"},
    )
    assert resp.status_code == 400


def test_status_invalid_transition(client, created_system):
    """Cannot go from Draft directly to Expired."""
    create_resp = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "Invalid"},
    )
    aid = create_resp.json()["id"]

    resp = client.patch(
        f"/api/assessments/{aid}/status",
        json={"status": "expired"},
    )
    assert resp.status_code == 400


def test_preview_template(client):
    resp = client.get("/api/assessments/templates/high")
    assert resp.status_code == 200
    data = resp.json()
    assert "sections" in data
    assert data["risk_tier"] == "high"
