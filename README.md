# English Learning App

Backend-приложение для изучения английского языка.
Предоставляет API для работы с грамматикой, словарями пользователя, переводом слов и игровыми механиками для запоминания лексики.

## Основные возможности

* Регистрация и аутентификация пользователей
* OAuth2 авторизация через VK ID
* Просмотр грамматических тем
* Перевод слов через Google Translate
* Создание персональных словарей
* Категории для организации слов
* Изучение слов в игровой форме (квизы, случайные слова)
* Добавление слов в избранное
* Работа с изображениями для слов

## Технологический стек

Backend:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy 2.0
* Pydantic
* OAuth 2.0
* Pytest

Frontend (простые страницы):

* Bootstrap 5

Инфраструктура:

* Docker
* Docker Compose

Приложение полностью асинхронное.

---

## Демо

Приложение доступно на сервере:

* Swagger документация (API): https://icodeit.ru/docs
* Фронтенд интерфейс: https://icodeit.ru/
---

# Установка и запуск

## 1. Клонирование репозитория

```
git clone https://github.com/Ridmovies/vocabulary-builder.git
cd vocabulary-builder
```

---

## 2. Настройка переменных окружения

Приложение использует два файла окружения:

* `.env` — для локального запуска
* `.env.docker` — для запуска через Docker

В репозитории находятся шаблоны конфигурации:

```
.env.example
.env.docker.example
```

Необходимо скопировать их и создать рабочие файлы.

---

### Локальная разработка

```
cp .env.example .env
```

Пример `.env.example`:

```
# Application mode
MODE=DEV

# JWT
SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/vocabulary
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/vocab_test

# VK OAuth
VK_OAUTH_CLIENT_ID=your_vk_client_id
VK_OAUTH_CLIENT_SECRET=your_vk_client_secret
VK_OAUTH_SERVICE_KEY=your_vk_service_key
VK_OAUTH_REDIRECT_URI=http://localhost/api/auth/callback/vkontakte

# Yandex Cloud
YANDEX_CLOUD_ACCESS_KEY=your_access_key
YANDEX_CLOUD_SECRET_KEY=your_secret_key
```

---

### Docker запуск

```
cp .env.docker.example .env.docker
```

Пример `.env.docker.example`:

```
MODE=DEV

# PostgreSQL
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=english_app

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/english_app

# JWT
SECRET_KEY=your_secret_key_here

# VK OAuth
VK_OAUTH_CLIENT_ID=your_vk_client_id
VK_OAUTH_CLIENT_SECRET=your_vk_client_secret
VK_OAUTH_SERVICE_KEY=your_vk_service_key
VK_OAUTH_REDIRECT_URI=http://localhost/api/auth/callback/vkontakte

# Yandex Cloud
YANDEX_CLOUD_ACCESS_KEY=your_access_key
YANDEX_CLOUD_SECRET_KEY=your_secret_key
```

`.env` и `.env.docker` не должны попадать в репозиторий и должны быть добавлены в `.gitignore`.

---

## 3. Запуск через Docker

Сборка и запуск контейнеров:

```
docker-compose up --build
```

После запуска сервис будет доступен:

```
http://localhost:8000
```

Swagger документация:

```
http://localhost:8000/docs
```

---

# API

## Users

Регистрация пользователя.

```
POST /api/users/register
```

---

## Auth

Аутентификация пользователя.

```
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

---

## VK OAuth

Авторизация через VK ID.

```
GET /api/auth/vk/get_auth_url
```

Получить ссылку для авторизации через VK.

```
GET /api/auth/callback/vkontakte
```

Callback endpoint для VK OAuth.

---

## Grammar

Работа с грамматическими темами.

```
GET /api/grammar/topics
GET /api/grammar/topics/{slug}
```

---

## Translate

Перевод текста.

```
POST /api/translate
```

---

## Words

Работа со словами пользователя.

```
GET    /api/words
POST   /api/words
GET    /api/words/{word_id}
PUT    /api/words/{word_id}
DELETE /api/words/{word_id}
```

Работа с изображениями слов.

```
POST   /api/words/{word_id}/image
DELETE /api/words/{word_id}/image
```

Избранные слова.

```
GET    /api/words/favorites
POST   /api/words/favorites/{word_id}
DELETE /api/words/favorites/{word_id}
```

Игровые режимы.

```
GET  /api/words/random
GET  /api/words/quick
POST /api/words/check
```

Квиз.

```
GET  /api/words/quiz
POST /api/words/quiz
```

---

## Categories

Категории для слов.

```
GET    /api/categories
POST   /api/categories
DELETE /api/categories/{category_id}
```

---

## Web Endpoints

Используются веб-интерфейсом.

```
GET  /api/web/random
POST /api/web/check
```

---

## Dev Endpoints

Служебные endpoints для разработки.

```
GET    /api/dev
GET    /api/dev/check-database
GET    /api/dev/db-info
DELETE /api/dev/reset-database
```

---

# Тестирование

Запуск тестов:

```
pytest
```

---

# Архитектура

Приложение построено по слоистой архитектуре:

```
api
services
repositories
models
schemas
core
```

* **API** — слой роутеров FastAPI
* **Services** — бизнес-логика
* **Repositories** — работа с базой данных
* **Models** — ORM модели SQLAlchemy
* **Schemas** — Pydantic схемы
* **Core** — конфигурация и инфраструктурный код

---

# Планы развития

* Добавление spaced repetition алгоритма
* Улучшение игровой механики
* Добавление статистики изучения слов
* Расширение грамматических материалов
* Поддержка нескольких языков


## VK OAuth (локальная разработка)

Инструкция по запуску VK авторизации локально:
docs/vk_oauth_local_setup.md
