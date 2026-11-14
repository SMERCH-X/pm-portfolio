# DuplicateHunter

Оценка схожести отчетов. Самостоятельный учебный сервис экосистемы BountyOS.

## Запуск
```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -q
```
API: http://localhost:8000/docs. Для Docker: `docker build -t duplicate-hunter . && docker run -p 8000:8000 duplicate-hunter`.

## API
- `GET /health`
- `POST /api/v1/comparisons`
- `GET /api/v1/comparisons`
- `GET /api/v1/comparisons/{id}`
- `GET /api/v1/audit`

## Пример тела запроса
```json
{
  "report_id": "example",
  "candidate_id": "example",
  "text_a": "example",
  "text_b": "example"
}
```

## Product brief
**Проблема:** оценка схожести отчетов.
**Пользователи:** bug bounty program manager, triage analyst, security researcher (в зависимости от роли).
**MVP:** API, локальное хранение, аудит и доменная операция.
**Следующая итерация:** RBAC, PostgreSQL, webhook-подписки, UI, контрактные и интеграционные тесты.
**Ограничения:** демонстрационная реализация, не предназначена для обработки реальных конфиденциальных отчетов.
