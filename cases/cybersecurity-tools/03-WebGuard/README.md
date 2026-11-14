# WebGuard

Учебная проверка HTTP security headers, HTTPS и отдельных `Set-Cookie` атрибутов.

```powershell
# Сначала в другом терминале: python -m http.server 8000
python webguard.py http://127.0.0.1:8000 --json report.json
python -m unittest discover -v
```

Выполняет обычный GET, без эксплуатации уязвимостей. Проверяйте только свои сайты или сайты с разрешением. Наличие заголовков не гарантирует безопасность; отсутствие отдельных заголовков не всегда ошибка. Проверка cookie-флагов эвристическая.
