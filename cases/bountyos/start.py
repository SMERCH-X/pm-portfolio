"""Run all five services and the unified BountyOS web app."""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVICES = [("bounty-scope",8101),("report-flow",8102),("duplicate-hunter",8103),("bounty-score",8104),("bounty-pulse",8105),("bountyos-web",8080)]
processes = []
try:
    for folder, port in SERVICES:
        process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app" if folder == "bountyos-web" else "app.main:app", "--host", "127.0.0.1", "--port", str(port)], cwd=ROOT/folder)
        processes.append(process)
    time.sleep(2)
    print("BountyOS: http://127.0.0.1:8080")
    webbrowser.open("http://127.0.0.1:8080")
    while True:
        time.sleep(1)
        for process in processes:
            if process.poll() is not None:
                raise RuntimeError(f"A service stopped (exit {process.returncode}). Check terminal output.")
except KeyboardInterrupt:
    print("Stopping BountyOS...")
finally:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try: process.wait(timeout=4)
        except subprocess.TimeoutExpired: process.kill()
