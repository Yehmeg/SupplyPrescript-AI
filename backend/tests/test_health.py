import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health(self, async_client: AsyncClient):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_ready(self, async_client: AsyncClient):
        response = await async_client.get("/ready")
        # May be 200 or 503 depending on whether artifacts load in test env
        assert response.status_code in (200, 503)
        data = response.json()
        if response.status_code == 200:
            assert data["status"] == "ready"
            assert "models_loaded" in data
            assert isinstance(data["models_loaded"], list)
        else:
            assert "detail" in data