from dockprompt.ir import DockPromptIR, DockRegion, DisplayGeometry, Intent
from dockprompt.postprocess import apply_effect, zoom_resize, screen_to_source, source_to_screen


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
    src = screen_to_source(0, 1026, 3840, 2400, 1920, 1080)
    back = source_to_screen(*src, 3840, 2400, 1920, 1080)
    assert abs(back[0] - 0) <= 1
    assert abs(back[1] - 1026) <= 1


def test_source_to_screen_4k_bottom():
    # 3840x2400 -> 1920x1080: width decides, scale 0.5, 60px cropped top and bottom.
    # Source y=2280 is the last visible row: 2280*0.5 - 60 = 1080.
    assert source_to_screen(0, 2280, 3840, 2400, 1920, 1080) == (0, 1080)


def test_screen_to_source_4k_bottom():
    # Dock top at screen y=1026: (1026 + 60) / 0.5 = 2172.
    # The old answer (1686, "70% of 2400") ignored that the width sets the scale.
    assert screen_to_source(0, 1026, 3840, 2400, 1920, 1080) == (0, 2172)


def test_screen_to_source_square_ai_output():
    # A 1024x1024 image (typical AI output) on 1920x1080: scale 1920/1024 = 1.875,
    # scaled 1920x1920, crop_y = (1920-1080)//2 = 420.
    # Dock band y=1026..1080 -> (1026+420)/1.875 = 771.2 and (1080+420)/1.875 = 800.
    assert screen_to_source(0, 1026, 1024, 1024, 1920, 1080) == (0, 771)
    assert screen_to_source(1920, 1080, 1024, 1024, 1920, 1080) == (1024, 800)


def test_screen_to_source_left_dock_uses_x():
    # Left dock 72px wide: x = 72/1.875 = 38.4; its full height is source y 224..800.
    assert screen_to_source(0, 0, 1024, 1024, 1920, 1080) == (0, 224)
    assert screen_to_source(72, 1080, 1024, 1024, 1920, 1080) == (38, 800)


def test_map_no_dock():
    dk = DockRegion(edge="none")
    assert dk.x == 0
    assert dk.y == 0
    assert dk.width == 0
    assert dk.height == 0


def _bottom_dock_ir(effect: str) -> DockPromptIR:
    return DockPromptIR(
        display=DisplayGeometry(width=1920, height=1080),
        dock=DockRegion(edge="bottom", x=0, y=1026, width=1920, height=54),
        intent=Intent(effect=effect),
    )


def test_apply_reports_dock_in_source_for_square_input(tmp_path):
    from PIL import Image
    src = tmp_path / "ai.png"
    Image.new("RGB", (1024, 1024), (200, 200, 200)).save(src)
    result = apply_effect(str(src), str(tmp_path / "out.png"), _bottom_dock_ir("blur"))
    assert result["dock_in_source"] == "x=0..1024 y=771..800"


def test_tint_keeps_light_lighter_than_dark(tmp_path):
    from PIL import Image
    src = tmp_path / "split.png"
    img = Image.new("RGB", (1920, 1080), (0, 0, 0))
    img.paste((255, 255, 255), (960, 0, 1920, 1080))  # right half white
    img.save(src)
    out = tmp_path / "out.png"
    apply_effect(str(src), str(out), _bottom_dock_ir("tint"))
    res = Image.open(out).convert("RGB")
    dark, light = res.getpixel((100, 1050)), res.getpixel((1800, 1050))
    assert sum(light) > sum(dark) + 200   # was inverted: white became (0,0,0)
    assert dark[2] > dark[0]              # the wash is blue
    assert res.getpixel((1800, 500)) == (255, 255, 255)  # outside the dock untouched
