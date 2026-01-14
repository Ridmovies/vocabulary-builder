import pytest


@pytest.mark.asyncio
async def test_registration(async_client):
    reg_data = {"email": "user_pytest@example.com", "username": "user_pytest", "password": "string"}
    response = await async_client.post("/api/users/register", json=reg_data)
    assert response.status_code == 201, response.text

@pytest.mark.asyncio
async def test_registration_login(async_client):
    reg_data = {"email": "user_pytest@example.com", "username": "user_pytest", "password": "string"}
    response = await async_client.post("/api/users/register", json=reg_data)
    assert response.status_code == 201, response.text

    log_data = {"email": "user_pytest@example.com", "password": "string"}
    response = await async_client.post("/api/auth/login", json=log_data)
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_get_me(auth_client):
    response = await auth_client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "user_pytest"
    assert response.json()["email"] == "user_pytest@example.com"


@pytest.mark.asyncio
async def test_logout(auth_client):
    # 1️⃣ Проверяем, что защищённый эндпоинт работает до logout
    response = await auth_client.get("/api/auth/me")
    assert response.status_code == 200
    data_before = response.json()
    assert data_before["email"] == "user_pytest@example.com"

    # 2️⃣ Логаут
    response = await auth_client.post("/api/auth/logout")
    assert response.status_code == 200  # или 204, в зависимости от реализации

    # 3️⃣ Проверяем, что токен больше не работает
    response = await auth_client.get("/api/auth/me")
    assert response.status_code == 401  # Unauthorized