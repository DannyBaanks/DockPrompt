import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_inspect_runs():
    r = subprocess.run(
        [sys.executable, "-m", "dockprompt", "inspect"],
        capture_output=True, text=True, timeout=10,
        cwd=ROOT,
    )
    assert r.returncode == 0
    assert "Display:" in r.stdout


def test_json_output():
    r = subprocess.run(
        [sys.executable, "-m", "dockprompt", "--json", "--effect", "blur"],
        capture_output=True, text=True, timeout=10,
        cwd=ROOT,
    )
    # exits 0 even with no display (geometry comes back as zeros), so a
    # failure here is a real regression, not a headless machine
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "display" in data
    assert "dock" in data
