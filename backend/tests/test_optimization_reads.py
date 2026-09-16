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
# SHARED FAKE DATA
# ============================================================

FAKE_RUN = SimpleNamespace(
    run_id=1,
    request_id="real-optimizer-test-001",
    optimization_status="Optimal",
    total_intervention_cost=900.0,
    total_expected_saving=197.60,
    created_at=datetime(
        2026, 9, 12, 11, 56, 11
    ),
)


FAKE_RECOMMENDATION = SimpleNamespace(
    recommendation_id=1,
    run_id=1,
    prediction_id=1,
    shipment_id="ORDER-1",
    action_id="A2",
    selected_action="PRIORITY_HANDLING",
    late_probability=0.548798,
    risk_after=0.439038,
    action_cost=900.0,
    baseline_expected_loss=5487.98,
    optimized_expected_cost=5290.384,
    expected_saving=197.596,
    predicted_time_days=4.0,
    created_at=datetime(
        2026, 9, 12, 11, 56, 11
    ),
)


# ============================================================
# TEST 1
# GET OPTIMIZATION RUN
# ============================================================

def test_get_optimization_run(monkeypatch):

    monkeypatch.setattr(
        crud,
        "get_optimization_run",
        lambda db, run_id: FAKE_RUN,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/optimization-runs/1"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["run_id"] == 1

        assert (
            data["request_id"]
            == "real-optimizer-test-001"
        )

        assert (
            data["optimization_status"]
            == "Optimal"
        )

        assert (
            data["total_intervention_cost"]
            == 900.0
        )

        assert (
            data["total_expected_saving"]
            == 197.60
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 2
# OPTIMIZATION RUN NOT FOUND
# ============================================================

def test_get_optimization_run_not_found(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_optimization_run",
        lambda db, run_id: None,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/optimization-runs/999"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "Optimization run not found"
            )
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 3
# GET RECOMMENDATION
# ============================================================

def test_get_recommendation(monkeypatch):

    monkeypatch.setattr(
        crud,
        "get_recommendation",
        lambda db, recommendation_id:
        FAKE_RECOMMENDATION,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/recommendations/1"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["recommendation_id"]
            == 1
        )

        assert data["run_id"] == 1

        assert (
            data["prediction_id"]
            == 1
        )

        assert (
            data["shipment_id"]
            == "ORDER-1"
        )

        assert (
            data["action_id"]
            == "A2"
        )

        assert (
            data["selected_action"]
            == "PRIORITY_HANDLING"
        )

        assert (
            data["late_probability"]
            == 0.548798
        )

        assert (
            data["risk_after"]
            == 0.439038
        )

        assert (
            data["action_cost"]
            == 900.0
        )

        assert (
            data["expected_saving"]
            == 197.596
        )

        assert (
            data["predicted_time_days"]
            == 4.0
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 4
# RECOMMENDATION NOT FOUND
# ============================================================

def test_get_recommendation_not_found(
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

        response = client.get(
            "/api/v1/recommendations/999"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Recommendation not found"
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 5
# GET RUN + RECOMMENDATIONS
# ============================================================

def test_get_recommendations_for_run(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_optimization_run",
        lambda db, run_id: FAKE_RUN,
    )

    monkeypatch.setattr(
        crud,
        "get_recommendations_for_run",
        lambda db, run_id: [
            FAKE_RECOMMENDATION
        ],
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/"
            "optimization-runs/1/"
            "recommendations"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["run"]["run_id"]
            == 1
        )

        assert (
            data["run"][
                "optimization_status"
            ]
            == "Optimal"
        )

        assert (
            len(data["recommendations"])
            == 1
        )

        recommendation = (
            data["recommendations"][0]
        )

        assert (
            recommendation[
                "recommendation_id"
            ]
            == 1
        )

        assert (
            recommendation[
                "selected_action"
            ]
            == "PRIORITY_HANDLING"
        )

        assert (
            recommendation[
                "prediction_id"
            ]
            == 1
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 6
# RECOMMENDATION HISTORY FOR MISSING RUN
# ============================================================

def test_get_recommendations_for_missing_run(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_optimization_run",
        lambda db, run_id: None,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    try:

        client = TestClient(app)

        response = client.get(
            "/api/v1/"
            "optimization-runs/999/"
            "recommendations"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "Optimization run not found"
            )
        }

    finally:

        app.dependency_overrides.clear()