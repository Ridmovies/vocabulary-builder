import pytest


# @pytest.mark.asyncio
# async def test_database_is_test_postgres(async_client):
#     # ACT
#     response = await async_client.get("/api/dev/db-info")
#
#     # ASSERT
#     assert response.status_code == 200
#
#     data = response.json()
#
#     assert data["dialect"] == "postgresql"
#     assert data["driver"] == "asyncpg"
#
#     # важная проверка — что это test БД
#     assert data["url"].endswith("/vocab_test")
#
#     # защита от ошибки: чтобы случайно не использовать прод
#     assert "localhost" in data["url"]


@pytest.mark.asyncio
async def test_registration(async_client):
    reg_data = {"email": "user_pytest@example.com", "username": "user_pytest", "password": "string"}
    response = await async_client.post("/api/users/register", json=reg_data)
    assert response.status_code == 201, response.text

@pytest.mark.asyncio
async def test_db_session_rollback(async_client):
    reg_data = {"email": "user_pytest@example.com", "username": "user_pytest", "password": "string"}
    response = await async_client.post("/api/users/register", json=reg_data)
    assert response.status_code == 201, response.text
