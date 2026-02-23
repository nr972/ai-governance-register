"""Tests for version history / audit logging."""


def test_create_generates_audit_log(client, created_system):
    resp = client.get(f"/api/systems/{created_system['id']}/history")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "created"
    assert logs[0]["entity_type"] == "ai_system"


def test_update_generates_audit_log(client, created_system):
    client.put(
        f"/api/systems/{created_system['id']}",
        json={"name": "New Name"},
    )

    resp = client.get(f"/api/systems/{created_system['id']}/history")
    logs = resp.json()
    # Most recent first
    update_log = logs[0]
    assert update_log["action"] == "updated"
    assert "name" in update_log["changes"]
    assert update_log["changes"]["name"]["old"] == created_system["name"]
    assert update_log["changes"]["name"]["new"] == "New Name"


def test_update_only_changed_fields_in_diff(client, created_system):
    """Only fields that actually changed should appear in the diff."""
    client.put(
        f"/api/systems/{created_system['id']}",
        json={"name": "Changed Only This"},
    )

    resp = client.get(f"/api/systems/{created_system['id']}/history")
    update_log = resp.json()[0]
    changes = update_log["changes"]
    assert "name" in changes
    # description didn't change, shouldn't be in diff
    assert "description" not in changes


def test_history_reverse_chronological(client, created_system):
    """History should be newest first."""
    client.put(
        f"/api/systems/{created_system['id']}", json={"name": "V2"}
    )
    client.put(
        f"/api/systems/{created_system['id']}", json={"name": "V3"}
    )

    resp = client.get(f"/api/systems/{created_system['id']}/history")
    logs = resp.json()
    assert len(logs) >= 3  # created + 2 updates
    # Verify most recent first
    assert logs[0]["action"] == "updated"
    assert logs[-1]["action"] == "created"


def test_history_pagination(client, created_system):
    for i in range(5):
        client.put(
            f"/api/systems/{created_system['id']}",
            json={"name": f"V{i}"},
        )

    resp = client.get(
        f"/api/systems/{created_system['id']}/history",
        params={"skip": 0, "limit": 2},
    )
    assert len(resp.json()) == 2


def test_history_not_found(client):
    resp = client.get("/api/systems/nonexistent/history")
    assert resp.status_code == 404
