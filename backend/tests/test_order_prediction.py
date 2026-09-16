from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from app.ml.service import get_ml_service
from app.db import crud
from app.api.schemas.prediction import PredictionResponseItem


# ============================================================
# VALID SAMPLE ORDER
# ============================================================

VALID_ORDER = {
    "Type": "DEBIT",
    "Days for shipment (scheduled)": 4,
    "Benefit per order": 91.25,
    "Sales per customer": 314.64,
    "Category Name": "Sporting Goods",
    "Customer City": "Chicago",
    "Customer Country": "EE. UU.",
    "Customer Segment": "Consumer",
    "Customer State": "Illinois",
    "Department Name": "Fitness",

    "Latitude": 41.8781,
    "Longitude": -87.6298,

    "Market": "USCA",
    "Order City": "New York City",
    "Order Country": "Estados Unidos",

    "Order Item Discount": 13.11,
    "Order Item Discount Rate": 0.04,
    "Order Item Product Price": 327.75,
    "Order Item Profit Ratio": 0.29,
    "Order Item Quantity": 1,

    "Sales": 327.75,
    "Order Item Total": 314.64,
    "Order Profit Per Order": 91.25,

    "Order Region": "East of USA",
    "Order State": "New York",

    "Product Category Id": 73,
    "Product Name": "Smart watch",
    "Product Price": 327.75,

    "Order_Year": 2026,
    "Order_Month": 9,
    "Order_DayOfWeek": 2,
    "Order_Day": 12,

    # Optional field
    "Order Status": "COMPLETE",
}


# ============================================================
# FAKE DATABASE DEPENDENCY
# ============================================================

def fake_get_db():
    yield object()


# ============================================================
# FAKE ML SERVICE - ELIGIBLE PREDICTION
# ============================================================

class FakeEligibleMLService:

    threshold = 0.22

    def predict(self, orders):

        return [
            PredictionResponseItem(
                Late_Risk_Probability=0.407488,
                Predicted_Late_Risk=1,
                Prediction_Eligible=True,
                Exclusion_Reason=None,
            )
            for _ in orders
        ]


# ============================================================
# TEST 1
# ORDER -> ML -> ORDER DB -> PREDICTION DB
# ============================================================

def test_order_prediction_persists_order_and_prediction(
    monkeypatch,
):

    inserted_orders = []
    inserted_predictions = []

    # --------------------------------------------------------
    # Mock orders table insert
    # --------------------------------------------------------

    def fake_insert_order(
        db,
        payload,
        source_system="api",
    ):

        inserted_orders.append(
            {
                "payload": payload,
                "source_system": source_system,
            }
        )

        return SimpleNamespace(
            order_id=101
        )

    # --------------------------------------------------------
    # Mock ml_predictions table insert
    # --------------------------------------------------------

    def fake_insert_ml_prediction(
        db,
        **kwargs,
    ):

        inserted_predictions.append(
            kwargs
        )

        return SimpleNamespace(
            prediction_id=201
        )

    monkeypatch.setattr(
        crud,
        "insert_order",
        fake_insert_order,
    )

    monkeypatch.setattr(
        crud,
        "insert_ml_prediction",
        fake_insert_ml_prediction,
    )

    # --------------------------------------------------------
    # Override FastAPI dependencies
    # --------------------------------------------------------

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    app.dependency_overrides[
        get_ml_service
    ] = lambda: FakeEligibleMLService()

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/orders/predict",
            json={
                "request_id": "db-test-001",
                "orders": [
                    VALID_ORDER
                ],
            },
        )

        assert response.status_code == 200

        data = response.json()

        # ----------------------------------------------------
        # API response
        # ----------------------------------------------------

        assert data["request_id"] == "db-test-001"

        assert (
            data["model_version"]
            == "SupplyPrescript ML V2"
        )

        assert data["threshold_used"] == 0.22

        assert len(data["predictions"]) == 1

        result = data["predictions"][0]

        assert result["order_id"] == 101

        assert result["prediction_id"] == 201

        assert (
            result["Late_Risk_Probability"]
            == 0.407488
        )

        assert (
            result["Predicted_Late_Risk"]
            == 1
        )

        assert (
            result["Prediction_Eligible"]
            is True
        )

        assert (
            result["Exclusion_Reason"]
            is None
        )

        # ----------------------------------------------------
        # Verify order persistence call
        # ----------------------------------------------------

        assert len(inserted_orders) == 1

        stored_order = inserted_orders[0]

        assert (
            stored_order["source_system"]
            == "api"
        )

        assert (
            stored_order["payload"]["Type"]
            == "DEBIT"
        )

        assert (
            stored_order["payload"][
                "Days for shipment (scheduled)"
            ]
            == 4
        )

        # ----------------------------------------------------
        # Verify prediction persistence call
        # ----------------------------------------------------

        assert len(inserted_predictions) == 1

        stored_prediction = (
            inserted_predictions[0]
        )

        assert (
            stored_prediction["order_id"]
            == 101
        )

        assert (
            stored_prediction[
                "model_version"
            ]
            == "SupplyPrescript ML V2"
        )

        assert (
            stored_prediction[
                "late_risk_probability"
            ]
            == 0.407488
        )

        assert (
            stored_prediction[
                "predicted_late_risk"
            ]
            is True
        )

        assert (
            stored_prediction[
                "prediction_eligible"
            ]
            is True
        )

        assert (
            stored_prediction[
                "threshold_used"
            ]
            == 0.22
        )

        assert (
            stored_prediction[
                "ensemble_models_used"
            ]
            == [
                "XGBoost",
                "LightGBM",
                "CatBoost",
            ]
        )

        assert (
            stored_prediction[
                "request_id"
            ]
            == "db-test-001"
        )

    finally:

        app.dependency_overrides.clear()


# ============================================================
# FAKE ML SERVICE - EXCLUDED ORDER
# ============================================================

class FakeExcludedMLService:

    threshold = 0.22

    def predict(self, orders):

        return [
            PredictionResponseItem(
                Late_Risk_Probability=None,
                Predicted_Late_Risk=None,
                Prediction_Eligible=False,
                Exclusion_Reason=(
                    "Non-shipment order status"
                ),
            )
            for _ in orders
        ]


# ============================================================
# TEST 2
# EXCLUDED ORDER IS SAVED,
# BUT NO INVALID ML PREDICTION IS INVENTED
# ============================================================

def test_excluded_order_does_not_insert_prediction(
    monkeypatch,
):

    insert_order_calls = []
    insert_prediction_calls = []

    def fake_insert_order(
        db,
        payload,
        source_system="api",
    ):

        insert_order_calls.append(
            payload
        )

        return SimpleNamespace(
            order_id=102
        )

    def fake_insert_ml_prediction(
        db,
        **kwargs,
    ):

        insert_prediction_calls.append(
            kwargs
        )

        return SimpleNamespace(
            prediction_id=999
        )

    monkeypatch.setattr(
        crud,
        "insert_order",
        fake_insert_order,
    )

    monkeypatch.setattr(
        crud,
        "insert_ml_prediction",
        fake_insert_ml_prediction,
    )

    app.dependency_overrides[get_db] = (
        fake_get_db
    )

    app.dependency_overrides[
        get_ml_service
    ] = lambda: FakeExcludedMLService()

    excluded_order = VALID_ORDER.copy()

    excluded_order[
        "Order Status"
    ] = "CANCELED"

    try:

        client = TestClient(app)

        response = client.post(
            "/api/v1/orders/predict",
            json={
                "request_id": "db-test-002",
                "orders": [
                    excluded_order
                ],
            },
        )

        assert response.status_code == 200

        data = response.json()

        result = data["predictions"][0]

        # Order itself is still stored.
        assert result["order_id"] == 102

        # No prediction row should be invented.
        assert result["prediction_id"] is None

        assert (
            result["Late_Risk_Probability"]
            is None
        )

        assert (
            result["Predicted_Late_Risk"]
            is None
        )

        assert (
            result["Prediction_Eligible"]
            is False
        )

        assert (
            result["Exclusion_Reason"]
            == "Non-shipment order status"
        )

        assert len(insert_order_calls) == 1

        # Critical check:
        # excluded prediction must NOT be written.
        assert len(
            insert_prediction_calls
        ) == 0

    finally:

        app.dependency_overrides.clear()