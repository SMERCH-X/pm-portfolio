# PySentry
AST-based static security checker for Python. Finds selected risky APIs and likely hardcoded credentials, reports line numbers and can export SARIF 2.1.0.

Checks: `eval`, `exec`, `subprocess` with `shell=True`, `pickle.load(s)`, `yaml.load`, MD5, SHA-1 and simple hardcoded-secret patterns.

```bash
python pysentry.py ./src --sarif report.sarif
python -m unittest -v
```
Educational SAST prototype, not a replacement for Bandit, Semgrep or code review. Findings are heuristic and require human validation; no findings does not prove code is secure.
