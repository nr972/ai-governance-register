"""Tests for PDF and DOCX export."""


def test_export_pdf(client, created_system):
    assess = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "PDF Export Test"},
    ).json()

    resp = client.get(f"/api/assessments/{assess['id']}/export/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "content-disposition" in resp.headers
    # PDF magic bytes
    assert resp.content[:4] == b"%PDF"


def test_export_docx(client, created_system):
    assess = client.post(
        "/api/assessments",
        json={"system_id": created_system["id"], "title": "DOCX Export Test"},
    ).json()

    resp = client.get(f"/api/assessments/{assess['id']}/export/docx")
    assert resp.status_code == 200
    assert "wordprocessingml" in resp.headers["content-type"]
    assert "content-disposition" in resp.headers
    # DOCX is a ZIP (PK magic bytes)
    assert resp.content[:2] == b"PK"


def test_export_not_found(client):
    resp = client.get("/api/assessments/nonexistent/export/pdf")
    assert resp.status_code == 404

    resp = client.get("/api/assessments/nonexistent/export/docx")
    assert resp.status_code == 404
