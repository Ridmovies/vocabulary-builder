## Локальная разработка с VK OAuth

VK ID предъявляет ограничения к `redirect_uri`. Для локальной разработки необходимо использовать **домен `localhost` и порт `80`**. Использование `127.0.0.1` или нестандартных портов может приводить к ошибкам валидации домена.

### 1. Настройка `redirect_uri`

В `.env` должен быть указан адрес callback:

`VK_OAUTH_REDIRECT_URI=http://localhost/api/auth/callback/vkontakte`

Этот же URL необходимо добавить в настройках приложения VK ID в разделе **Redirect URI**.

Важно:
VK проверяет точное совпадение домена. `localhost` и `127.0.0.1` считаются разными origin.

---

### 2. Освобождение 80 порта

VK OAuth корректно работает только с `80` портом, поэтому локальный сервер должен быть доступен по `http://localhost`.

Если Apache уже занимает порт 80, его необходимо остановить:

`sudo systemctl stop apache2`

После этого запустить nginx:

`sudo systemctl start nginx`

---

### 3. Проксирование через nginx

Backend обычно работает на `8000` порту (например FastAPI / Uvicorn).
Nginx должен проксировать входящие запросы с `80` порта на backend.

Пример конфигурации nginx:

```
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

После изменения конфигурации nginx необходимо перезапустить:

`sudo systemctl restart nginx`

---

### 4. Запуск backend

Backend запускается на стандартном порту разработки:

`uvicorn app.main:app --host 127.0.0.1 --port 8000`

После этого приложение будет доступно по адресу:

`http://localhost`

---

### 5. Поток авторизации

1. Пользователь нажимает кнопку **Войти через VK**.
2. Frontend вызывает `/api/auth/vk/get_auth_url`.
3. Backend генерирует ссылку VK OAuth (PKCE + state).
4. Браузер перенаправляется на `https://id.vk.com/authorize`.
5. После успешного входа VK делает redirect на

`http://localhost/api/auth/callback/vkontakte`

6. Backend обменивает `code` на токены VK, создаёт или авторизует пользователя.
7. Устанавливаются auth cookies (`access`, `refresh`, `csrf`).
8. Пользователь редиректится обратно на frontend.

---

### 6. Проверка

Открыть в браузере:

`http://localhost/login`

Нажать **Войти через VK** и пройти стандартный OAuth flow.

