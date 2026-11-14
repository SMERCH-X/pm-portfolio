# BountyPulse

События и аналитика программы. Самостоятельный учебный сервис экосистемы BountyOS.

## Запуск
```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -q
```
API: http://localhost:8000/docs. Для Docker: `docker build -t bounty-pulse . && docker run -p 8000:8000 bounty-pulse`.

## API
- `GET /health`
- `POST /api/v1/events`
- `GET /api/v1/events`
- `GET /api/v1/events/{id}`
- `GET /api/v1/audit`

## Пример тела запроса
```json
{
  "report_id": "example",
  "event_type": "example",
  "program_id": "example"
}
```

## Product brief
**Проблема:** события и аналитика программы.
**Пользователи:** bug bounty program manager, triage analyst, security researcher (в зависимости от роли).
**MVP:** API, локальное хранение, аудит и доменная операция.
**Следующая итерация:** RBAC, PostgreSQL, webhook-подписки, UI, контрактные и интеграционные тесты.
**Ограничения:** демонстрационная реализация, не предназначена для обработки реальных конфиденциальных отчетов.
