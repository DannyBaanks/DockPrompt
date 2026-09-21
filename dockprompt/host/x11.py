from dockprompt.host.detect import (
    detect_desktop_environment,
    detect_display_x11,
    detect_session_type,
    detect_workarea_x11,
)
from dockprompt.ir import DisplayGeometry, Workarea


def inspect_host() -> tuple:
    """Return (display, workarea, de, session_type)."""
    de = detect_desktop_environment()
    session = detect_session_type()
    display = detect_display_x11()
    workarea = detect_workarea_x11()
    return display, workarea, de, session
