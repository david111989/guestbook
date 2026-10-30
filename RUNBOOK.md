# RUNBOOK: аварийная инструкция

Заменяйте `OWNER/REPO` на ваш логин и имя репозитория GitHub (маленькими буквами).

## 1. Проверить, что сервис жив

```bash
curl http://localhost:8000/health      # ожидаем {"status":"ok"}
curl http://localhost:8000/version     # какая версия сейчас запущена
docker compose ps                      # app и db должны быть healthy
docker compose logs app --tail 50      # последние логи сервиса
```

## 2. Выкатить новую версию

1. Обновите `CHANGELOG.md`, закоммитьте и запушьте в `main`, дождитесь зелёного CI.
2. Поставьте тег и запушьте его:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
3. В GitHub → Actions дождитесь зелёного запуска, в Packages появится образ `1.1.0`.
4. Запустите эту версию:
   TAG=1.1.0 docker compose up -d
   Локально проще: в `compose.yaml` заменить `build: .` на `image: ghcr.io/OWNER/REPO:1.1.0`
   и выполнить `docker compose up -d`.

## 3. Откат на предыдущую версию

Если новая версия сломалась (`/health` не отвечает, в логах ошибки):

1. Остановите новую версию: `docker compose down` (данные в volume `db_data` сохраняются).
2. Запустите предыдущий тег:
   TAG=1.0.0 docker compose up -d.
3. Проверьте: `curl http://localhost:8000/version` показывает `1.0.0`, `/health` отвечает `ok`.

Откат безопасен для данных: миграции только добавляют (`IF NOT EXISTS`) и ничего не удаляют,
поэтому старая версия работает на базе, которую уже трогала новая.

## 4. Частые проблемы

| Симптом | Что делать |
|---------|-----------|
| `app` не стартует, в логах `connection refused` | база ещё не готова: `docker compose ps`, подождите `healthy` у `db` |
| `password authentication failed` | пароль в `.env` не совпадает с тем, с которым создан volume: `docker compose down -v` (удалит данные!) и запустите заново |
| CI красный из-за Ruff | `uv run ruff check . --fix` и закоммитьте |
| Нет образа в Packages | CI не зелёный, или пуш был не в `main` и не по тегу `vX.Y.Z` |
| `docker pull` пишет `denied` | пакет приватный: GitHub → Packages → ваш пакет → Package settings → сделать Public |
