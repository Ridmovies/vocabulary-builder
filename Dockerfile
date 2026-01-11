FROM python:3.12-slim

# 1. Отключаем лишнее
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1

# 2. Рабочая директория
WORKDIR /app

# 3. Системные зависимости (часто нужны для psycopg2, pillow и т.п.)
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    && rm -rf /var/lib/apt/lists/*

# 4. Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем код
COPY . .

# 6. Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
