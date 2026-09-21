from dockprompt.ir import DockRegion, DisplayGeometry
from dockprompt.postprocess import zoom_resize, screen_to_source_y, source_to_screen_y


def test_zoom_resize_16x9_to_16x9():
    sw, sh, cx, cy, s = zoom_resize(1672, 941, 1920, 1080)
    assert sw == 1920
    assert sh == 1081  # rounding from 941 * 1.1483
    assert cx == 0
    assert cy == 0


def test_zoom_resize_4k_to_1080():
    sw, sh, cx, cy, s = zoom_resize(3840, 2400, 1920, 1080)
    assert sw == 1920
    assert sh == 1200
    assert cx == 0
    assert cy == 60


def test_zoom_resize_wide_to_1080():
    sw, sh, cx, cy, s = zoom_resize(2560, 1080, 1920, 1080)
    assert sh == 1080
    assert cy == 0


def test_screen_to_source_roundtrip_4k():
    # Screen y=1026 → source → back to screen should be stable
    src_y = screen_to_source_y(1026, 2400, 1080)
    back = source_to_screen_y(src_y, 2400, 1080)
    assert abs(back - 1026) <= 1


def test_source_to_screen_4k_bottom():
    # Source y=2280 (bottom of 2400) should map near screen bottom
    sy = source_to_screen_y(2280, 2400, 1080)
    assert sy >= 1000


def test_screen_to_source_4k_bottom():
    # Screen y=1026 (dock top) in4k source → y=1686 (70% of 2400)
    src_y = screen_to_source_y(1026, 2400, 1080)
    assert 1600 < src_y < 1800


def test_map_no_dock():
    dk = DockRegion(edge="none")
    assert dk.x == 0
    assert dk.y == 0
    assert dk.width == 0
    assert dk.height == 0
