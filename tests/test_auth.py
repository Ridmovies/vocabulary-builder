import pytest


@pytest.mark.asyncio
async def test_protected_route(async_client):
    response = await async_client.get("/api/dev")
    assert response.status_code == 200

