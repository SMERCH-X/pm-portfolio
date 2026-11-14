# Cybersecurity Portfolio — 5 учебных инструментов на Python

Пять самостоятельных небольших проектов для практики Python и основ анализа безопасности. **Не коммерческие продукты и не полноценные средства защиты.** Запускайте сетевые проверки только на своих ресурсах или с явного разрешения владельца.

| Проект | Что делает | Зависимости |
|---|---|---|
| [LogSentinel](01-LogSentinel/) | Анализ SSH authentication log | Стандартная библиотека |
| [NetScope](02-NetScope/) | TCP connect scan одного хоста | Стандартная библиотека |
| [WebGuard](03-WebGuard/) | Проверка HTTP security headers и cookies | Стандартная библиотека |
| [PCAP Analyzer](04-PCAP-Analyzer/) | Офлайн-анализ TCP-пакетов из PCAP | Стандартная библиотека |
| [PySentry](05-PySentry/) | Статический анализ Python AST | Стандартная библиотека |

## Запуск и тесты (Windows PowerShell)

Установите Python 3.10+ и откройте PowerShell в распакованной папке `cybersecurity_portfolio`.

```powershell
cd 01-LogSentinel
python logsentinel.py sample_auth.log --threshold 5 --window 10 --json alerts.json
python -m unittest discover -v
cd ..

cd 02-NetScope
python netscope.py 127.0.0.1 --ports 1-100 --timeout 0.3 --json scan.json
python -m unittest discover -v
cd ..

cd 03-WebGuard
python webguard.py http://127.0.0.1:8000 --json report.json
python -m unittest discover -v
cd ..

cd 04-PCAP-Analyzer
python pcap_analyzer.py sample.pcap --port-threshold 3 --syn-threshold 4 --json findings.json
python -m unittest discover -v
cd ..

cd 05-PySentry
python pysentry.py pysentry.py --sarif report.sarif
python -m unittest discover -v
```

**Примечания:** для WebGuard требуется запущенный HTTP-сервер на указанном адресе (например, `python -m http.server 8000` в другом терминале). Для PCAP Analyzer включён искусственный `sample.pcap`; поддерживается только классический Ethernet PCAP. Сетевые команды не обращаются к сторонним целям в примерах. `python` на Windows может называться `py`.

Все проверки эвристические и могут ошибаться. Подробности и ограничения — в README каждого проекта.
