from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from app.api.routes import writeback


# ------------------------------------------------------------
# Fake DB dependency
# ------------------------------------------------------------

def override_get_db():
    yield object()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================
# 1. EXECUTE DECISION
# ============================================================

def test_execute_decision(monkeypatch):

    fake_decision = SimpleNamespace(
        decision_id=101,
        status="executed",
    )

    def fake_execute_decision(
        db,
        recommendation_id,
        shipment_id,
        executed_by,
        predicted_cost_at_exec,
        predicted_time_at_exec,
    ):
        assert recommendation_id == 1
        assert shipment_id == 10
        assert executed_by == "demo-user"
        assert predicted_cost_at_exec == 1800
        assert predicted_time_at_exec == 2.5

        return fake_decision

    monkeypatch.setattr(
        writeback.crud,
        "execute_decision",
        fake_execute_decision,
    )

    response = client.post(
        "/api/v1/decisions/execute",
        json={
            "recommendation_id": 1,
            "shipment_id": 10,
            "executed_by": "demo-user",
            "predicted_cost_at_exec": 1800,
            "predicted_time_at_exec": 2.5,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "decision_id": 101,
        "status": "executed",
    }


# ============================================================
# 2. DECISION HISTORY
# ============================================================

def test_decision_history(monkeypatch):

    fake_decisions = [
        SimpleNamespace(
            decision_id=101,
            shipment_id=10,
            status="executed",
            executed_by="demo-user",
            executed_at=datetime(
                2026, 9, 5, 10, 30, 0
            ),
            predicted_cost_at_exec=1800,
            predicted_time_at_exec=2.5,
        )
    ]

    def fake_history(
        db,
        shipment_id=None,
    ):
        assert shipment_id == 10
        return fake_decisions

    monkeypatch.setattr(
        writeback.crud,
        "get_decision_history",
        fake_history,
    )

    response = client.get(
        "/api/v1/decisions/history",
        params={"shipment_id": 10},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["decision_id"] == 101
    assert data[0]["shipment_id"] == 10
    assert data[0]["status"] == "executed"
    assert data[0]["executed_by"] == "demo-user"
    assert data[0]["predicted_cost_at_exec"] == 1800.0
    assert data[0]["predicted_time_at_exec"] == 2.5


# ============================================================
# 3. RECORD OUTCOME
# ============================================================

def test_record_outcome(monkeypatch):

    fake_outcome = SimpleNamespace(
        outcome_id=501,
    )

    def fake_insert_outcome(
        db,
        decision_id,
        actual_cost,
        actual_time_days,
        actual_delayed,
    ):
        assert decision_id == 101
        assert actual_cost == 1600
        assert actual_time_days == 2.0
        assert actual_delayed is False

        return fake_outcome

    monkeypatch.setattr(
        writeback.crud,
        "insert_outcome",
        fake_insert_outcome,
    )

    response = client.post(
        "/api/v1/outcomes",
        json={
            "decision_id": 101,
            "actual_cost": 1600,
            "actual_time_days": 2.0,
            "actual_delayed": False,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "outcome_id": 501
    }


# ============================================================
# 4. SINGLE DECISION ROI
# ============================================================

def test_decision_roi(monkeypatch):

    fake_roi = {
        "decision_id": 101,
        "shipment_id": 10,
        "predicted_cost": 1800.0,
        "actual_cost": 1600.0,
        "cost_savings": 200.0,
        "predicted_time_days": 2.5,
        "actual_time_days": 2.0,
        "actual_delayed": False,
    }

    monkeypatch.setattr(
        writeback.crud,
        "get_decision_roi",
        lambda db, decision_id: fake_roi,
    )

    response = client.get(
        "/api/v1/decisions/101/roi"
    )

    assert response.status_code == 200

    assert response.json()["cost_savings"] == 200.0
    assert response.json()["actual_delayed"] is False


# ============================================================
# 5. ROI - DECISION NOT FOUND
# ============================================================

def test_decision_roi_not_found(monkeypatch):

    monkeypatch.setattr(
        writeback.crud,
        "get_decision_roi",
        lambda db, decision_id: None,
    )

    response = client.get(
        "/api/v1/decisions/999/roi"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Decision not found"
    }


# ============================================================
# 6. ALL ROI
# ============================================================

def test_all_roi(monkeypatch):

    fake_results = [
        {
            "decision_id": 101,
            "shipment_id": 10,
            "predicted_cost": 1800.0,
            "actual_cost": 1600.0,
            "cost_savings": 200.0,
        },
        {
            "decision_id": 102,
            "shipment_id": 11,
            "status": "outcome_pending",
        },
    ]

    monkeypatch.setattr(
        writeback.crud,
        "get_all_roi",
        lambda db: fake_results,
    )

    response = client.get(
        "/api/v1/roi"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["decision_id"] == 101
    assert data[0]["cost_savings"] == 200.0

# ============================================================
# 7. CREATE SHIPMENT
# ============================================================

def test_create_shipment(monkeypatch):

    fake_shipment = SimpleNamespace(
        shipment_id=1001,
        origin="Bhubaneswar",
        destination="Kolkata",
    )

    def fake_insert_shipment(db, shipment_data):
        assert shipment_data["origin"] == "Bhubaneswar"
        assert shipment_data["destination"] == "Kolkata"
        assert shipment_data["carrier"] == "Demo Carrier"
        assert shipment_data["product_type"] == "Electronics"
        assert shipment_data["quantity"] == 10

        return fake_shipment

    monkeypatch.setattr(
        writeback.crud,
        "insert_shipment",
        fake_insert_shipment,
    )

    response = client.post(
        "/api/v1/shipments",
        json={
            "origin": "Bhubaneswar",
            "destination": "Kolkata",
            "carrier": "Demo Carrier",
            "product_type": "Electronics",
            "quantity": 10,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "shipment_id": 1001,
        "origin": "Bhubaneswar",
        "destination": "Kolkata",
    }