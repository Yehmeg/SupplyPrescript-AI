from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import (
    app,
    get_db,
    get_optimization_service,
)
from app.db import crud
from app.api.schemas.optimization import RecommendationItem


# ============================================================
# FAKE DB
# ============================================================

def fake_get_db():
    yield object()


# ============================================================
# FAKE OPTIMIZER
# ============================================================

class FakeOptimizationService:

    def optimize(
        self,
        shipments,
        constraints,
    ):
        return (
            "Optimal",
            [
                RecommendationItem(
                    shipment_id="ORDER-1",
                    action_id="A1",
                    selected_action="EXPEDITE",
                    late_probability=0.548798,
                    risk_after=0.356719,
                    action_cost=1800.0,
                    baseline_expected_loss=5487.98,
                    optimized_expected_cost=5367.19,
                    expected_saving=120.79,
                    predicted_time_days=3.0,
                )
            ],
            1800.0,
            120.79,
        )


# ============================================================
# COMMON REQUEST
# ============================================================

OPTIMIZE_REQUEST = {
    "request_id": "optimizer-db-test-001",
    "shipments": [
        {
            "shipment_id": "ORDER-1",
            "late_probability": 0.548798,
            "late_penalty": 10000.0,
            "baseline_time_days": 5.0,
            "expedite_available": True,
            "priority_available": True,
            "route_available": True,
            "hub_available": True,
        }
    ],
    "constraints": {
        "total_budget": 10000.0,
        "expedite_capacity": 1,
        "priority_capacity": 1,
        "route_capacity": 1,
        "hub_capacity": 1,
    },
    "prediction_ids": [1],
}


# ============================================================
# TEST 1
# OPTIMIZER RESULT IS PERSISTED
# ============================================================

def test_optimize_persists_run_and_recommendation(
    monkeypatch,
):

    run_calls = []
    recommendation_calls = []

    # --------------------------------------------------------
    # Existing ML prediction must be found
    # --------------------------------------------------------

    def fake_get_prediction(
        db,
        prediction_id,
    ):
        assert prediction_id == 1

        return SimpleNamespace(
            prediction_id=1
        )

    # --------------------------------------------------------
    # Fake optimization_runs insert
    # --------------------------------------------------------

    def fake_insert_optimization_run(
        db,
        **kwargs,
    ):
        run_calls.append(kwargs)

        return SimpleNamespace(
            run_id=301
        )

    # --------------------------------------------------------
    # Fake optimization_recommendations insert
    # --------------------------------------------------------

    def fake_insert_optimization_recommendations(
        db,
        *,
        run_id,
        prediction_ids,
        recommendations,
    ):
        recommendation_calls.append(
            {
                "run_id": run_id,
                "prediction_ids": prediction_ids,
                "recommendations": recommendations,
            }
        )

        return [
            SimpleNamespace(
                recommendation_id=401
            )
        ]

    monkeypatch.setattr(
        crud,
        "get_prediction",
        fake_get_prediction,
    )

    monkeypatch.setattr(
        crud,
        "insert_optimization_run",
        fake_insert_optimization_run,
    )

    monkeypatch.setattr(
        crud,
        "insert_optimization_recommendations",
        fake_insert_optimization_recommendations,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    app.dependency_overrides[
        get_optimization_service
    ] = lambda: FakeOptimizationService()

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/optimize",
            json=OPTIMIZE_REQUEST,
        )

        assert response.status_code == 200

        data = response.json()

        # ----------------------------------------------------
        # API response
        # ----------------------------------------------------

        assert (
            data["request_id"]
            == "optimizer-db-test-001"
        )

        assert (
            data["optimization_status"]
            == "Optimal"
        )

        assert (
            data["total_intervention_cost"]
            == 1800.0
        )

        assert (
            data["total_expected_saving"]
            == 120.79
        )

        assert (
            data["recommendation_ids"]
            == [401]
        )

        assert (
            len(data["recommendations"])
            == 1
        )

        recommendation = (
            data["recommendations"][0]
        )

        assert (
            recommendation["shipment_id"]
            == "ORDER-1"
        )

        assert (
            recommendation["selected_action"]
            == "EXPEDITE"
        )

        # ----------------------------------------------------
        # optimization_runs insert
        # ----------------------------------------------------

        assert len(run_calls) == 1

        run = run_calls[0]

        assert (
            run["request_id"]
            == "optimizer-db-test-001"
        )

        assert (
            run["optimization_status"]
            == "Optimal"
        )

        assert (
            run["total_intervention_cost"]
            == 1800.0
        )

        assert (
            run["total_expected_saving"]
            == 120.79
        )

        # ----------------------------------------------------
        # recommendations insert
        # ----------------------------------------------------

        assert (
            len(recommendation_calls)
            == 1
        )

        stored = recommendation_calls[0]

        assert stored["run_id"] == 301

        assert (
            stored["prediction_ids"]
            == [1]
        )

        assert (
            len(stored["recommendations"])
            == 1
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 2
# prediction_ids COUNT MUST MATCH shipments
# ============================================================

def test_prediction_id_count_must_match_shipments():

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    app.dependency_overrides[
        get_optimization_service
    ] = lambda: FakeOptimizationService()

    bad_request = {
        **OPTIMIZE_REQUEST,
        "prediction_ids": [1, 2],
    }

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/optimize",
            json=bad_request,
        )

        assert response.status_code == 422

        assert response.json() == {
            "detail": (
                "prediction_ids count must match "
                "shipments count"
            )
        }

    finally:

        app.dependency_overrides.clear()


# ============================================================
# TEST 3
# UNKNOWN PREDICTION ID RETURNS 404
# ============================================================

def test_optimize_unknown_prediction(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_prediction",
        lambda db, prediction_id: None,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    app.dependency_overrides[
        get_optimization_service
    ] = lambda: FakeOptimizationService()

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/optimize",
            json={
                **OPTIMIZE_REQUEST,
                "prediction_ids": [999],
            },
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Prediction 999 not found"
        }

    finally:

        app.dependency_overrides.clear()