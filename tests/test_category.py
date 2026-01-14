import pytest


@pytest.mark.asyncio
async def test_get_categories(auth_client, seed_categories):
    response = await auth_client.get("/api/categories")
    assert response.status_code == 200
    assert type(response.json()) == list
    assert len(response.json()) == 3