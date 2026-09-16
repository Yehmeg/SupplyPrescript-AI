import pytest
from httpx import AsyncClient


MOCK_SHIPMENTS = [
    {"shipment_id": "S001", "late_probability": 0.90, "late_penalty": 15000, "expedite_available": True, "priority_available": True, "route_available": True, "hub_available": False},
    {"shipment_id": "S002", "late_probability": 0.75, "late_penalty": 10000, "expedite_available": True, "priority_available": True, "route_available": True, "hub_available": False},
    {"shipment_id": "S003", "late_probability": 0.60, "late_penalty": 8000, "expedite_available": False, "priority_available": True, "route_available": True, "hub_available": True},
    {"shipment_id": "S004", "late_probability": 0.40, "late_penalty": 12000, "expedite_available": True, "priority_available": True, "route_available": False, "hub_available": False},
    {"shipment_id": "S005", "late_probability": 0.25, "late_penalty": 5000, "expedite_available": True, "priority_available": False, "route_available": True, "hub_available": True},
]


@pytest.mark.asyncio
async def test_optimize_locked_checkpoint(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/optimize",
        json={
            "request_id": "opt-test-1",
            "shipments": MOCK_SHIPMENTS,
            "constraints": {
                "total_budget": 10000,
                "expedite_capacity": 1,
                "priority_capacity": 1,
                "route_capacity": 1,
                "hub_capacity": 1,
            },
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["optimization_status"] == "Optimal"
    assert data["total_intervention_cost"] == pytest.approx(4100.0)
    assert data["total_expected_saving"] == pytest.approx(3685.0)
    assert len(data["recommendations"]) == 5


@pytest.mark.asyncio
async def test_optimize_empty_shipments_rejected(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/optimize",
        json={"shipments": []},
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_optimize_returns_predicted_time_days(
    async_client: AsyncClient,
):
    response = await async_client.post(
        "/api/v1/optimize",
        json={
            "request_id": "time-test-1",
            "shipments": [
                {
                    "shipment_id": "S001",
                    "late_probability": 0.90,
                    "late_penalty": 15000,
                    "baseline_time_days": 5.0,
                    "expedite_available": True,
                    "priority_available": True,
                    "route_available": True,
                    "hub_available": False,
                }
            ],
            "constraints": {
                "total_budget": 10000,
                "expedite_capacity": 1,
                "priority_capacity": 1,
                "route_capacity": 1,
                "hub_capacity": 1,
            },
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert len(data["recommendations"]) == 1

    recommendation = data["recommendations"][0]

    assert "predicted_time_days" in recommendation
    assert recommendation["predicted_time_days"] is not None
    assert recommendation["predicted_time_days"] >= 0

