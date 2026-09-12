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
# ACCEPT RECOMMENDATION
# ============================================================

def test_accept_recommendation(monkeypatch):

    fake_recommendation = SimpleNamespace(
        recommendation_id=1
    )

    fake_decision = SimpleNamespace(
        decision_id=101,
        recommendation_id=1,
        decision_status="ACCEPTED",
        execution_status="PENDING",
        decided_by="test-user",
        decision_note="Proceed with action",
        decided_at=datetime(
            2026, 9, 12, 12, 30, 0
        ),
        executed_at=None,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        fake_recommendation,
    )

    monkeypatch.setattr(
        crud,
        "get_decision_for_recommendation",
        lambda db, recommendation_id: None,
    )

    def fake_insert_decision(
        db,
        *,
        recommendation_id,
        decision_status,
        decided_by=None,
        decision_note=None,
    ):
        assert recommendation_id == 1
        assert decision_status == "ACCEPTED"
        assert decided_by == "test-user"
        assert (
            decision_note
            == "Proceed with action"
        )

        return fake_decision

    monkeypatch.setattr(
        crud,
        "insert_recommendation_decision",
        fake_insert_decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations/1/decision",
            json={
                "decision_status": "ACCEPTED",
                "decided_by": "test-user",
                "decision_note": (
                    "Proceed with action"
                ),
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["decision_id"] == 101

        assert (
            data["recommendation_id"]
            == 1
        )

        assert (
            data["decision_status"]
            == "ACCEPTED"
        )

        assert (
            data["execution_status"]
            == "PENDING"
        )

        assert (
            data["decided_by"]
            == "test-user"
        )

        assert (
            data["decision_note"]
            == "Proceed with action"
        )

        assert data["executed_at"] is None

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 2
# REJECT RECOMMENDATION
# ============================================================

def test_reject_recommendation(monkeypatch):

    fake_recommendation = SimpleNamespace(
        recommendation_id=1
    )

    fake_decision = SimpleNamespace(
        decision_id=102,
        recommendation_id=1,
        decision_status="REJECTED",
        execution_status="NOT_APPLICABLE",
        decided_by="test-user",
        decision_note="Too expensive",
        decided_at=datetime(
            2026, 9, 12, 12, 35, 0
        ),
        executed_at=None,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        fake_recommendation,
    )

    monkeypatch.setattr(
        crud,
        "get_decision_for_recommendation",
        lambda db, recommendation_id: None,
    )

    def fake_insert_decision(
        db,
        *,
        recommendation_id,
        decision_status,
        decided_by=None,
        decision_note=None,
    ):
        assert recommendation_id == 1
        assert decision_status == "REJECTED"

        return fake_decision

    monkeypatch.setattr(
        crud,
        "insert_recommendation_decision",
        fake_insert_decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations/1/decision",
            json={
                "decision_status": "REJECTED",
                "decided_by": "test-user",
                "decision_note": "Too expensive",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["decision_status"]
            == "REJECTED"
        )

        assert (
            data["execution_status"]
            == "NOT_APPLICABLE"
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 3
# DUPLICATE DECISION
# ============================================================

def test_duplicate_decision(monkeypatch):

    fake_recommendation = SimpleNamespace(
        recommendation_id=1
    )

    existing_decision = SimpleNamespace(
        decision_id=101
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        fake_recommendation,
    )

    monkeypatch.setattr(
        crud,
        "get_decision_for_recommendation",
        lambda db, recommendation_id:
        existing_decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations/1/decision",
            json={
                "decision_status": "ACCEPTED"
            },
        )

        assert response.status_code == 409

        assert response.json() == {
            "detail": (
                "A decision already exists "
                "for this recommendation"
            )
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 4
# RECOMMENDATION NOT FOUND
# ============================================================

def test_decision_recommendation_not_found(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id: None,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations/999/decision",
            json={
                "decision_status": "ACCEPTED"
            },
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Recommendation not found"
        }

    finally:

        app.dependency_overrides.clear()

# ============================================================
# TEST 5
# EXECUTE ACCEPTED PENDING DECISION
# ============================================================

def test_execute_accepted_decision(
    monkeypatch,
):

    pending_decision = SimpleNamespace(
        decision_id=101,
        recommendation_id=1,
        decision_status="ACCEPTED",
        execution_status="PENDING",
        decided_by="test-user",
        decision_note="Proceed",
        decided_at=datetime(
            2026, 9, 12, 12, 30, 0
        ),
        executed_at=None,
    )

    executed_decision = SimpleNamespace(
        decision_id=101,
        recommendation_id=1,
        decision_status="ACCEPTED",
        execution_status="EXECUTED",
        decided_by="test-user",
        decision_note="Proceed",
        decided_at=datetime(
            2026, 9, 12, 12, 30, 0
        ),
        executed_at=datetime(
            2026, 9, 12, 13, 0, 0
        ),
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        pending_decision,
    )

    monkeypatch.setattr(
        crud,
        "mark_decision_executed",
        lambda db, decision_id:
        executed_decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/101/execute"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["decision_id"] == 101

        assert (
            data["decision_status"]
            == "ACCEPTED"
        )

        assert (
            data["execution_status"]
            == "EXECUTED"
        )

        assert data["executed_at"] is not None

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 6
# REJECTED DECISION CANNOT EXECUTE
# ============================================================

def test_rejected_decision_cannot_execute(
    monkeypatch,
):

    rejected_decision = SimpleNamespace(
        decision_id=102,
        decision_status="REJECTED",
        execution_status="NOT_APPLICABLE",
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        rejected_decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/102/execute"
        )

        assert response.status_code == 409

        assert response.json() == {
            "detail": (
                "Rejected recommendation "
                "cannot be executed"
            )
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 7
# ALREADY EXECUTED
# ============================================================

def test_decision_already_executed(
    monkeypatch,
):

    decision = SimpleNamespace(
        decision_id=101,
        decision_status="ACCEPTED",
        execution_status="EXECUTED",
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id: decision,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/decisions/101/execute"
        )

        assert response.status_code == 409

        assert response.json() == {
            "detail": "Decision already executed"
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 8
# DECISION NOT FOUND
# ============================================================

def test_execute_missing_decision(
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
            "/api/v1/decisions/999/execute"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Decision not found"
        }

    finally:

        app.dependency_overrides.clear()