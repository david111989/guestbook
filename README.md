# Guestbook

Небольшой сервис «гостевая книга»: API на FastAPI + база PostgreSQL.
Проект показывает путь от коммита до прода: CI, публикация Docker-образа, релизы по тегам и откат.

## Быстрый старт (локально)

Нужен Docker Desktop.

```bash
cp .env.example .env        # затем откройте .env и поменяйте пароль
docker compose up --build
```

Проверка: откройте http://localhost:8000/health (должно быть `{"status":"ok"}`)
и http://localhost:8000/docs (интерактивная документация API).

## API

| Метод | Путь | Что делает |
|-------|------|-----------|
| GET | `/health` | сервис жив |
| GET | `/version` | версия запущенного образа |
| GET | `/messages` | последние 50 сообщений |
| POST | `/messages` | добавить сообщение `{"author": "...", "text": "..."}` |

## Разработка

```bash
uv sync                 # установить зависимости
uv run ruff check .     # линтер
uv run pytest           # тесты
```

## CI/CD и релизы

- На каждый `push` и `pull_request` запускаются Ruff и pytest.
- После зелёного CI из ветки `main` образ публикуется в ghcr.io с тегом `latest`.
- Релиз: тег `vX.Y.Z` (semver) собирает образ с этой версией.
  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```
- История изменений: [CHANGELOG.md](CHANGELOG.md).

## Если что-то сломалось

См. [RUNBOOK.md](RUNBOOK.md): там пошаговая аварийная инструкция и откат.
