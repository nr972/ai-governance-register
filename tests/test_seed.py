"""Tests for seed data loading."""


def test_seed_loads_data(client):
    resp = client.post("/api/seed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["systems_created"] == 6
    assert data["assessments_created"] == 4

    # Verify systems exist
    systems = client.get("/api/systems").json()
    assert len(systems) == 6

    # Verify assessments exist
    assessments = client.get("/api/assessments").json()
    assert len(assessments) == 4


def test_seed_is_idempotent(client):
    resp1 = client.post("/api/seed")
    assert resp1.json()["systems_created"] == 6

    resp2 = client.post("/api/seed")
    assert "already contains" in resp2.json()["message"]

    # Still only 6 systems
    systems = client.get("/api/systems").json()
    assert len(systems) == 6


def test_seeded_systems_have_correct_tiers(client):
    client.post("/api/seed")
    systems = client.get("/api/systems").json()

    tier_map = {s["name"]: s["risk_tier"] for s in systems}
    # Spot-check a few
    system_detail = None
    for s in systems:
        full = client.get(f"/api/systems/{s['id']}").json()
        if full["name"] == "FaceGate Access Control":
            assert full["risk_tier"] == "high"
        elif full["name"] == "SupportBot Pro":
            assert full["risk_tier"] == "limited"
        elif full["name"] == "ContentCurate Recommender":
            assert full["risk_tier"] == "minimal"


def test_seeded_assessments_linked_correctly(client):
    client.post("/api/seed")
    assessments = client.get("/api/assessments").json()

    for a in assessments:
        # Each assessment should link to a valid system
        system = client.get(f"/api/systems/{a['system_id']}").json()
        assert system is not None
        assert "id" in system
