from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from app.db import crud


# ============================================================
# FAKE DATABASE DEPENDENCY
# ============================================================

def fake_get_db():
    yield object()


# ============================================================
# TEST: GET ORDER
# ============================================================

def test_get_order_by_id(monkeypatch):

    fake_order = SimpleNamespace(
        order_id=101,
        order_status="COMPLETE",
        source_system="api",
        received_at=datetime(
            2026, 9, 12, 10, 0, 0
        ),
    )

    monkeypatch.setattr(
        crud,
        "get_order",
        lambda db, order_id: fake_order,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/orders/101"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["order_id"] == 101
        assert data["order_status"] == "COMPLETE"
        assert data["source_system"] == "api"

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TEST: ORDER NOT FOUND
# ============================================================

def test_get_order_not_found(monkeypatch):

    monkeypatch.setattr(
        crud,
        "get_order",
        lambda db, order_id: None,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/orders/999"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Order not found"
        }

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TEST: GET PREDICTION
# ============================================================

def test_get_prediction_by_id(monkeypatch):

    fake_prediction = SimpleNamespace(
        prediction_id=201,
        order_id=101,
        model_version="SupplyPrescript ML V2",
        late_risk_probability=0.407488,
        predicted_late_risk=True,
        prediction_eligible=True,
        exclusion_reason=None,
        threshold_used=0.22,
        ensemble_models_used=[
            "XGBoost",
            "LightGBM",
            "CatBoost",
        ],
        created_at=datetime(
            2026, 9, 12, 10, 1, 0
        ),
        request_id="db-test-001",
    )

    monkeypatch.setattr(
        crud,
        "get_prediction",
        lambda db, prediction_id: fake_prediction,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/predictions/201"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["prediction_id"] == 201
        assert data["order_id"] == 101

        assert (
            data["model_version"]
            == "SupplyPrescript ML V2"
        )

        assert (
            data["late_risk_probability"]
            == 0.407488
        )

        assert (
            data["predicted_late_risk"]
            is True
        )

        assert (
            data["prediction_eligible"]
            is True
        )

        assert data["threshold_used"] == 0.22

        assert data["ensemble_models_used"] == [
            "XGBoost",
            "LightGBM",
            "CatBoost",
        ]

        assert (
            data["request_id"]
            == "db-test-001"
        )

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TEST: PREDICTION NOT FOUND
# ============================================================

def test_get_prediction_not_found(monkeypatch):

    monkeypatch.setattr(
        crud,
        "get_prediction",
        lambda db, prediction_id: None,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/predictions/999"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Prediction not found"
        }

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TEST: ORDER + ALL PREDICTIONS
# ============================================================

def test_get_predictions_for_order(monkeypatch):

    fake_order = SimpleNamespace(
        order_id=101,
        order_status="COMPLETE",
        source_system="api",
        received_at=datetime(
            2026, 9, 12, 10, 0, 0
        ),
    )

    fake_predictions = [
        SimpleNamespace(
            prediction_id=201,
            order_id=101,
            model_version="SupplyPrescript ML V2",
            late_risk_probability=0.407488,
            predicted_late_risk=True,
            prediction_eligible=True,
            exclusion_reason=None,
            threshold_used=0.22,
            ensemble_models_used=[
                "XGBoost",
                "LightGBM",
                "CatBoost",
            ],
            created_at=datetime(
                2026, 9, 12, 10, 1, 0
            ),
            request_id="db-test-001",
        ),
        SimpleNamespace(
            prediction_id=202,
            order_id=101,
            model_version="SupplyPrescript ML V2",
            late_risk_probability=0.312500,
            predicted_late_risk=True,
            prediction_eligible=True,
            exclusion_reason=None,
            threshold_used=0.22,
            ensemble_models_used=[
                "XGBoost",
                "LightGBM",
                "CatBoost",
            ],
            created_at=datetime(
                2026, 9, 12, 11, 0, 0
            ),
            request_id="db-test-002",
        ),
    ]

    monkeypatch.setattr(
        crud,
        "get_order",
        lambda db, order_id: fake_order,
    )

    monkeypatch.setattr(
        crud,
        "get_predictions_for_order",
        lambda db, order_id: fake_predictions,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/orders/101/predictions"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["order"]["order_id"] == 101

        assert len(data["predictions"]) == 2

        assert (
            data["predictions"][0][
                "prediction_id"
            ]
            == 201
        )

        assert (
            data["predictions"][1][
                "prediction_id"
            ]
            == 202
        )

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TEST: ORDER HISTORY REQUEST FOR UNKNOWN ORDER
# ============================================================

def test_get_predictions_for_missing_order(
    monkeypatch,
):

    monkeypatch.setattr(
        crud,
        "get_order",
        lambda db, order_id: None,
    )

    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/orders/999/predictions"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Order not found"
        }

    finally:
        app.dependency_overrides.clear()