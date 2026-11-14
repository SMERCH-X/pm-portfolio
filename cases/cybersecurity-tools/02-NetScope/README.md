# NetScope
Bounded-concurrency TCP connect scanner for one authorized hostname/IP.

```bash
python netscope.py 127.0.0.1 --ports 1-1024 --timeout 0.3 --json scan.json
python -m unittest -v
```
No CIDR expansion or stealth modes. Scan only systems you own or have explicit permission to assess. `closed_or_filtered` intentionally does not claim to distinguish a closed port from firewall filtering or network failure.
