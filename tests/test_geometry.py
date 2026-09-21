from dockprompt.ir import DisplayGeometry, Workarea
from dockprompt.geometry.normalize import derive_dock_region


def test_bottom_dock():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(0, 32, 1920, 994)
    dk = derive_dock_region(d, w)
    assert dk.edge == "bottom"
    assert dk.height == 54
    assert dk.y == 1026
    assert dk.x == 0
    assert dk.width == 1920


def test_top_dock():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(0, 34, 1920, 1046)
    dk = derive_dock_region(d, w)
    assert dk.edge == "top"
    assert dk.height == 34
    assert dk.y == 0


def test_left_dock():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(100, 0, 1820, 1080)
    dk = derive_dock_region(d, w)
    assert dk.edge == "left"
    assert dk.width == 100


def test_right_dock():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(0, 0, 1870, 1080)
    dk = derive_dock_region(d, w)
    assert dk.edge == "right"
    assert dk.width == 50


def test_no_dock():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(0, 0, 1920, 1080)
    dk = derive_dock_region(d, w)
    assert dk.edge == "none"


def test_malformed_workarea_clamped():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(-10, -20, 3000, 2000)
    dk = derive_dock_region(d, w)
    assert dk.edge in ("top", "bottom", "left", "right", "none")


def test_multiple_reserved_edges_picks_largest():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(0, 50, 1920, 930)
    dk = derive_dock_region(d, w)
    assert dk.edge == "bottom"
    assert dk.height == 100


def test_zero_workarea():
    d = DisplayGeometry(1920, 1080)
    w = Workarea(0, 0, 0, 0)
    dk = derive_dock_region(d, w)
    assert dk.edge == "none"
