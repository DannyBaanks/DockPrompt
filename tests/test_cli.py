import json
import subprocess
import sys


def test_inspect_runs():
    r = subprocess.run(
        [sys.executable, "-m", "dockprompt", "inspect"],
        capture_output=True, text=True, timeout=10,
        cwd="/home/danny/Development/ISyCo Git/DockPrompt",
    )
    assert r.returncode == 0
    assert "Display:" in r.stdout


def test_json_output():
    r = subprocess.run(
        [sys.executable, "-m", "dockprompt", "--json", "--effect", "blur"],
        capture_output=True, text=True, timeout=10,
        cwd="/home/danny/Development/ISyCo Git/DockPrompt",
    )
    if r.returncode == 0:
        data = json.loads(r.stdout)
        assert "display" in data
        assert "dock" in data
