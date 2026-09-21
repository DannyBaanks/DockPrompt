import os
import re
import subprocess

from dockprompt.ir import DisplayGeometry, Workarea


def detect_desktop_environment() -> str:
    return os.environ.get(
        "XDG_CURRENT_DESKTOP", os.environ.get("DESKTOP_SESSION", "unknown")
    )


def detect_session_type() -> str:
    return os.environ.get("XDG_SESSION_TYPE", "unknown")


def detect_display_x11() -> DisplayGeometry:
    try:
        out = subprocess.check_output(
            ["xrandr", "--current"], text=True, timeout=5
        )
        for line in out.splitlines():
            if "*" in line:
                parts = line.split()[0]
                w, h = parts.split("x")
                return DisplayGeometry(width=int(w), height=int(h))
    except Exception:
        pass
    return DisplayGeometry()


def detect_workarea_x11() -> Workarea:
    try:
        out = subprocess.check_output(
            ["xprop", "-root", "_NET_WORKAREA"], text=True, timeout=5
        )
        m = re.search(r"=\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", out)
        if m:
            return Workarea(
                x=int(m.group(1)), y=int(m.group(2)),
                width=int(m.group(3)), height=int(m.group(4)),
            )
    except Exception:
        pass
    return Workarea()
