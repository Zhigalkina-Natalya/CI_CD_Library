# Базовый образ
FROM python:3.13-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY pyproject.toml poetry.lock* .

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем весь проект
COPY . .

# Открываем порт Django
EXPOSE 8000

# Команда запуска Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]