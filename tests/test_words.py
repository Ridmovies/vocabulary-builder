import pytest


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