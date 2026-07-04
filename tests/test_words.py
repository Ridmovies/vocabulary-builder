import pytest


async def _register_and_login(async_client, *, email: str, username: str):
    user_data = {"email": email, "username": username, "password": "string"}
    response = await async_client.post("/api/users/register", json=user_data)
    assert response.status_code == 201, response.text

    response = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": "string"},
    )
    assert response.status_code == 200, response.text


async def _create_word(async_client, *, english: str = "private", russian: str = "личное") -> int:
    response = await async_client.get("/api/categories")
    assert response.status_code == 200, response.text
    category_id = response.json()[0]["id"]

    response = await async_client.post(
        "/api/words",
        json={"english": english, "russian": russian, "category_ids": [category_id]},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.asyncio
async def test_get_words(auth_client):
    response = await auth_client.get('/api/words')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_word(auth_client, user_seed_data):
    response = await auth_client.get("/api/categories")
    assert response.status_code == 200, response.json
    cats = response.json()
    assert len(cats) > 0

    cat_id: int = cats[0]["id"]  # ✅ берем id первой категории

    word_json = {
          "english": "hello",
          "russian": "привет",
          "category_ids": [
            cat_id
          ]
    }
    response = await auth_client.post('/api/words', json=word_json)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_user_cannot_read_update_or_delete_another_users_word(async_client):
    await _register_and_login(
        async_client,
        email="owner_pytest@example.com",
        username="owner_pytest",
    )
    word_id = await _create_word(async_client)

    async_client.cookies.clear()
    await _register_and_login(
        async_client,
        email="intruder_pytest@example.com",
        username="intruder_pytest",
    )

    read_response = await async_client.get(f"/api/words/{word_id}")
    update_response = await async_client.put(
        f"/api/words/{word_id}",
        json={"english": "changed"},
    )
    delete_response = await async_client.delete(f"/api/words/{word_id}")

    assert read_response.status_code == 404
    assert update_response.status_code == 404
    assert delete_response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_favorite_or_check_another_users_word(async_client):
    await _register_and_login(
        async_client,
        email="favorite_owner_pytest@example.com",
        username="favorite_owner_pytest",
    )
    word_id = await _create_word(async_client, english="secret", russian="секрет")

    async_client.cookies.clear()
    await _register_and_login(
        async_client,
        email="favorite_intruder_pytest@example.com",
        username="favorite_intruder_pytest",
    )

    favorite_response = await async_client.post(f"/api/words/favorites/{word_id}")
    typing_response = await async_client.post(
        "/api/words/check",
        json={"word_id": word_id, "answer": "secret"},
    )

    assert favorite_response.status_code == 404
    assert typing_response.status_code == 404
