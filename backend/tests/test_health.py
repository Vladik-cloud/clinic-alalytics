from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_report_structure(monkeypatch):
    monkeypatch.setattr(
        "app.main.summary",
        lambda *a, **k: {
            "total_revenue": 1000,
            "doctors_count": 2,
            "avg_referral_rate_pct": 25,
            "period": {"start": None, "end": None},
        },
    )
    monkeypatch.setattr("app.main.revenue_by_doctor", lambda *a, **k: [])
    monkeypatch.setattr("app.main.referral_rate_by_doctor", lambda *a, **k: [])
    monkeypatch.setattr(
        "app.main.detect_schema",
        lambda: type(
            "S",
            (),
            {
                "doctors": "doctors",
                "visits": "visits",
                "revenue_table": "services",
            },
        )(),
    )
    response = client.get("/api/report")
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "revenue_by_doctor" in body
