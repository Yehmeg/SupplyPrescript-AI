import pytest
from httpx import AsyncClient
from app.ml.service import get_ml_service

class TestPredictEndpoint:
    @pytest.mark.asyncio
    async def test_predict_single_order(self, async_client: AsyncClient, sample_order):
        response = await async_client.post("/api/v1/predict", json={"orders": [sample_order]})
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "predictions" in data
        assert len(data["predictions"]) == 1
        assert data["model_version"] == "SupplyPrescript ML V2"
        assert data["threshold_used"] == pytest.approx(
            get_ml_service().threshold
        )

        pred = data["predictions"][0]
        assert "Prediction_Eligible" in pred
        assert isinstance(pred["Prediction_Eligible"], bool)
        assert "Late_Risk_Probability" in pred
        assert "Predicted_Late_Risk" in pred
        assert "Exclusion_Reason" in pred

    @pytest.mark.asyncio
    async def test_predict_multiple_orders(self, async_client: AsyncClient, sample_order):
        orders = [sample_order, {**sample_order, "Type": "TRANSFER"}]
        response = await async_client.post("/api/v1/predict", json={"orders": orders})
        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 2

    @pytest.mark.asyncio
    async def test_predict_empty_orders_rejected(self, async_client: AsyncClient):
        response = await async_client.post("/api/v1/predict", json={"orders": []})
        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_predict_missing_required_field_rejected(self, async_client: AsyncClient, sample_order):
        # Remove a required field
        bad_order = {k: v for k, v in sample_order.items() if k != "Type"}
        response = await async_client.post("/api/v1/predict", json={"orders": [bad_order]})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_predict_with_order_status_excluded(self, async_client: AsyncClient, sample_order):
        # CANCELED status should be excluded
        order = {**sample_order, "Order Status": "CANCELED"}
        response = await async_client.post("/api/v1/predict", json={"orders": [order]})
        assert response.status_code == 200
        data = response.json()
        pred = data["predictions"][0]
        assert pred["Prediction_Eligible"] is False
        assert pred["Exclusion_Reason"] == "Non-shipment order status"
        assert pred["Late_Risk_Probability"] is None
        assert pred["Predicted_Late_Risk"] is None

    @pytest.mark.asyncio
    async def test_predict_case_insensitive_status(self, async_client: AsyncClient, sample_order):
        order = {**sample_order, "Order Status": "canceled"}
        response = await async_client.post("/api/v1/predict", json={"orders": [order]})
        assert response.status_code == 200
        data = response.json()
        pred = data["predictions"][0]
        assert pred["Prediction_Eligible"] is False

    @pytest.mark.asyncio
    async def test_predict_request_id_echoed(self, async_client: AsyncClient, sample_order):
        request_id = "test-request-123"
        response = await async_client.post(
            "/api/v1/predict", json={"orders": [sample_order], "request_id": request_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == request_id

@pytest.mark.asyncio
async def test_predict_persists_when_shipment_id_supplied(
    async_client: AsyncClient,
    sample_order,
    monkeypatch,
):
    from types import SimpleNamespace
    from app.db import crud

    def fake_insert_prediction(
        db,
        shipment_id,
        risk_probability,
        predicted_class,
        model_version,
        eligibility_status="eligible",
    ):
        assert shipment_id == 1001
        assert 0 <= risk_probability <= 1
        assert predicted_class in ("delayed", "on_time")
        assert model_version == "SupplyPrescript ML V2"
        assert eligibility_status == "eligible"

        return SimpleNamespace(
            prediction_id=5001
        )

    monkeypatch.setattr(
        crud,
        "insert_prediction",
        fake_insert_prediction,
    )

    response = await async_client.post(
        "/api/v1/predict",
        json={
            "orders": [sample_order],
            "shipment_ids": [1001],
            "request_id": "persist-test-001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["request_id"] == "persist-test-001"
    assert data["prediction_ids"] == [5001]
    assert len(data["predictions"]) == 1