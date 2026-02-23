"""Tests for AI System CRUD endpoints."""


def test_create_system(client, sample_system_data):
    resp = client.post("/api/systems", json=sample_system_data)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == sample_system_data["name"]
    assert data["risk_tier"] == "minimal"
    assert data["id"]


def test_create_system_missing_fields(client):
    resp = client.post("/api/systems", json={"name": "Incomplete"})
    assert resp.status_code == 422


def test_create_system_invalid_enum(client, sample_system_data):
    sample_system_data["risk_tier"] = "nonexistent"
    resp = client.post("/api/systems", json=sample_system_data)
    assert resp.status_code == 422


def test_list_systems(client, created_system):
    resp = client.get("/api/systems")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == created_system["name"]


def test_list_systems_filter_risk_tier(client, created_system):
    resp = client.get("/api/systems", params={"risk_tier": "minimal"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    resp = client.get("/api/systems", params={"risk_tier": "high"})
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_list_systems_search(client, created_system):
    resp = client.get("/api/systems", params={"search": "Test AI"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_system(client, created_system):
    resp = client.get(f"/api/systems/{created_system['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == created_system["name"]


def test_get_system_not_found(client):
    resp = client.get("/api/systems/nonexistent-id")
    assert resp.status_code == 404


def test_update_system(client, created_system):
    resp = client.put(
        f"/api/systems/{created_system['id']}",
        json={"name": "Updated Name", "risk_tier": "high"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Name"
    assert data["risk_tier"] == "high"


def test_update_system_no_fields(client, created_system):
    resp = client.put(f"/api/systems/{created_system['id']}", json={})
    assert resp.status_code == 400


def test_update_system_not_found(client):
    resp = client.put(
        "/api/systems/nonexistent-id",
        json={"name": "X"},
    )
    assert resp.status_code == 404


def test_delete_system(client, created_system):
    resp = client.delete(f"/api/systems/{created_system['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/api/systems/{created_system['id']}")
    assert resp.status_code == 404


def test_delete_system_not_found(client):
    resp = client.delete("/api/systems/nonexistent-id")
    assert resp.status_code == 404


def test_system_pagination(client, sample_system_data):
    for i in range(5):
        data = dict(sample_system_data)
        data["name"] = f"System {i}"
        client.post("/api/systems", json=data)

    resp = client.get("/api/systems", params={"skip": 0, "limit": 2})
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp = client.get("/api/systems", params={"skip": 3, "limit": 10})
    assert resp.status_code == 200
    assert len(resp.json()) == 2
