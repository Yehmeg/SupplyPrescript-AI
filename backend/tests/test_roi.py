from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from app.db import crud


def fake_get_db():
    yield object()


FAKE_DECISION = SimpleNamespace(
    decision_id=1,
    recommendation_id=1,
    decision_status="ACCEPTED",
    execution_status="EXECUTED",
)


FAKE_RECOMMENDATION = SimpleNamespace(
    recommendation_id=1,
    selected_action="PRIORITY_HANDLING",

    baseline_expected_loss=5487.98,
    action_cost=900.0,
    optimized_expected_cost=5290.384,
    expected_saving=197.596,

    predicted_time_days=4.0,
)


FAKE_OUTCOME = SimpleNamespace(
    outcome_id=1,
    decision_id=1,

    actual_intervention_cost=850.0,
    actual_delay_cost=0.0,
    actual_total_cost=850.0,

    actual_time_days=3.8,
    actual_delayed=False,
)


# ============================================================
# TEST 1
# PREDICTED VS ACTUAL ROI
# ============================================================

def test_decision_roi(monkeypatch):

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id: FAKE_DECISION,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        FAKE_RECOMMENDATION,
    )

    monkeypatch.setattr(
        crud,
        "get_outcome_for_decision",
        lambda db, decision_id: FAKE_OUTCOME,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/decisions/1/roi"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["decision_id"] == 1
        assert data["recommendation_id"] == 1
        assert data["outcome_id"] == 1

        assert (
            data["selected_action"]
            == "PRIORITY_HANDLING"
        )

        # ----------------------------------------------------
        # Predicted
        # ----------------------------------------------------

        assert data[
            "baseline_expected_loss"
        ] == pytest.approx(5487.98)

        assert data[
            "predicted_action_cost"
        ] == pytest.approx(900.0)

        assert data[
            "optimized_expected_cost"
        ] == pytest.approx(5290.384)

        assert data[
            "predicted_expected_saving"
        ] == pytest.approx(197.596)

        assert data[
            "predicted_time_days"
        ] == pytest.approx(4.0)

        # ----------------------------------------------------
        # Actual
        # ----------------------------------------------------

        assert data[
            "actual_intervention_cost"
        ] == pytest.approx(850.0)

        assert data[
            "actual_delay_cost"
        ] == pytest.approx(0.0)

        assert data[
            "actual_total_cost"
        ] == pytest.approx(850.0)

        assert data[
            "actual_time_days"
        ] == pytest.approx(3.8)

        assert data[
            "actual_delayed"
        ] is False

        # ----------------------------------------------------
        # Variances
        # ----------------------------------------------------

        assert data[
            "intervention_cost_variance"
        ] == pytest.approx(
            850.0 - 900.0
        )

        assert data[
            "optimized_cost_variance"
        ] == pytest.approx(
            850.0 - 5290.384
        )

        realized_saving = (
            5487.98 - 850.0
        )

        assert data[
            "realized_savings_vs_baseline"
        ] == pytest.approx(
            realized_saving
        )

        assert data[
            "savings_variance"
        ] == pytest.approx(
            realized_saving - 197.596
        )

        assert data[
            "time_variance_days"
        ] == pytest.approx(
            3.8 - 4.0
        )

        expected_roi = (
            realized_saving
            / 850.0
        ) * 100.0

        assert data[
            "realized_roi_percent"
        ] == pytest.approx(
            expected_roi
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 2
# DECISION NOT FOUND
# ============================================================

def test_roi_decision_not_found(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id: None,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/decisions/999/roi"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Decision not found"
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 3
# RECOMMENDATION NOT FOUND
# ============================================================

def test_roi_recommendation_not_found(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        FAKE_DECISION,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id: None,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/decisions/1/roi"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Recommendation not found"
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 4
# OUTCOME NOT FOUND
# ============================================================

def test_roi_outcome_not_found(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        FAKE_DECISION,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        FAKE_RECOMMENDATION,
    )

    monkeypatch.setattr(
        crud,
        "get_outcome_for_decision",
        lambda db, decision_id: None,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/decisions/1/roi"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Outcome not found"
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 5
# ZERO INTERVENTION COST
# ROI SHOULD BE NULL INSTEAD OF DIVIDING BY ZERO
# ============================================================

def test_roi_zero_intervention_cost(
    monkeypatch,
):

    zero_cost_outcome = SimpleNamespace(
        outcome_id=2,
        decision_id=1,

        actual_intervention_cost=0.0,
        actual_delay_cost=0.0,
        actual_total_cost=0.0,

        actual_time_days=3.8,
        actual_delayed=False,
    )

    monkeypatch.setattr(
        crud,
        "get_decision",
        lambda db, decision_id:
        FAKE_DECISION,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        FAKE_RECOMMENDATION,
    )

    monkeypatch.setattr(
        crud,
        "get_outcome_for_decision",
        lambda db, decision_id:
        zero_cost_outcome,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/decisions/1/roi"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["realized_roi_percent"]
            is None
        )

    finally:

        app.dependency_overrides.clear()