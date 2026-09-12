from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from app.db import crud


# ============================================================
# FAKE DATABASE
# ============================================================

def fake_get_db():
    yield object()


# ============================================================
# TEST 1
# RECORD OUTCOME FOR EXECUTED DECISION
# ============================================================

def test_record_outcome_for_executed_decision(
    monkeypatch,
):

    executed_decision = SimpleNamespace(
        decision_id=1,
        recommendation_id=1,
        decision_status="ACCEPTED",
        execution_status="EXECUTED",
    )

    fake_outcome = SimpleNamespace(
        outcome_id=501,
        decision_id=1,
        actual_intervention_cost=850.0,
        actual_time_days=3.8,
        actual_delayed=False,
        actual_delay_cost=0.0,
        actual_total_cost=850.0,
        outcome_note="Delivered successfully",
        recorded_at=datetime(
            2026, 9, 12, 13, 0, 0
        ),
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        executed_decision,
    )

    monkeypatch.setattr(
        crud,
        "get_outcome_for_decision",
        lambda db, decision_id: None,
    )

    def fake_insert_outcome(
        db,
        *,
        decision_id,
        actual_intervention_cost,
        actual_time_days,
        actual_delayed,
        actual_delay_cost=0.0,
        outcome_note=None,
    ):
        assert decision_id == 1
        assert actual_intervention_cost == 850.0
        assert actual_time_days == 3.8
        assert actual_delayed is False
        assert actual_delay_cost == 0.0
        assert (
            outcome_note
            == "Delivered successfully"
        )

        return fake_outcome

    monkeypatch.setattr(
        crud,
        "insert_optimization_outcome",
        fake_insert_outcome,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/1/outcome",
            json={
                "actual_intervention_cost": 850.0,
                "actual_time_days": 3.8,
                "actual_delayed": False,
                "actual_delay_cost": 0.0,
                "outcome_note": (
                    "Delivered successfully"
                ),
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["outcome_id"] == 501
        assert data["decision_id"] == 1

        assert (
            data["actual_intervention_cost"]
            == 850.0
        )

        assert data["actual_time_days"] == 3.8

        assert data["actual_delayed"] is False

        assert data["actual_delay_cost"] == 0.0

        assert data["actual_total_cost"] == 850.0

        assert (
            data["outcome_note"]
            == "Delivered successfully"
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 2
# NON-EXECUTED DECISION CANNOT HAVE OUTCOME
# ============================================================

def test_outcome_requires_executed_decision(
    monkeypatch,
):

    pending_decision = SimpleNamespace(
        decision_id=1,
        decision_status="ACCEPTED",
        execution_status="PENDING",
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        pending_decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/1/outcome",
            json={
                "actual_intervention_cost": 850.0,
                "actual_time_days": 3.8,
                "actual_delayed": False,
                "actual_delay_cost": 0.0,
            },
        )

        assert response.status_code == 409

        assert response.json() == {
            "detail": (
                "Outcome can only be recorded "
                "for an executed decision"
            )
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 3
# DUPLICATE OUTCOME
# ============================================================

def test_duplicate_outcome(monkeypatch):

    executed_decision = SimpleNamespace(
        decision_id=1,
        decision_status="ACCEPTED",
        execution_status="EXECUTED",
    )

    existing_outcome = SimpleNamespace(
        outcome_id=501
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        executed_decision,
    )

    monkeypatch.setattr(
        crud,
        "get_outcome_for_decision",
        lambda db, decision_id:
        existing_outcome,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/1/outcome",
            json={
                "actual_intervention_cost": 850.0,
                "actual_time_days": 3.8,
                "actual_delayed": False,
                "actual_delay_cost": 0.0,
            },
        )

        assert response.status_code == 409

        assert response.json() == {
            "detail": (
                "An outcome already exists "
                "for this decision"
            )
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 4
# DECISION NOT FOUND
# ============================================================

def test_outcome_decision_not_found(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id: None,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/999/outcome",
            json={
                "actual_intervention_cost": 850.0,
                "actual_time_days": 3.8,
                "actual_delayed": False,
                "actual_delay_cost": 0.0,
            },
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Decision not found"
        }

    finally:

        app.dependency_overrides.clear()