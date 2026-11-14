# LogSentinel
SSH authentication log analyzer with a sliding-window heuristic for repeated failed logins.

```bash
python logsentinel.py sample_auth.log --threshold 5 --window 10 --json alerts.json
python -m unittest -v
```
Parses ISO-8601 timestamps in common sshd failed-login, invalid-user and accepted-login messages. Educational prototype, not a SIEM; validate alerts with surrounding events.
