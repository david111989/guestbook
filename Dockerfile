FROM python:3.12-slim

# uv берём из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 1. Сначала только файлы зависимостей: этот слой кэшируется,
#    пока pyproject.toml и uv.lock не меняются
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# 2. Потом код: он меняется чаще, поэтому идёт после зависимостей
COPY app ./app

# Версия образа (передаётся из CI при релизе по тегу)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000

# --host 0.0.0.0, иначе из-за пределов контейнера сервис недоступен
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
