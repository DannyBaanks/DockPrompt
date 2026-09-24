"""Deterministic post-processor: resize + apply effect to exact canvas coords."""
from pathlib import Path

from dockprompt.ir import DockPromptIR, DockRegion, DisplayGeometry

TINT_COLOR = (0, 0, 68)  # #000044
TINT_ALPHA = 0.45


def zoom_resize(img_w: int, img_h: int, target_w: int, target_h: int):
    """Compute scale + crop offset matching GNOME 'zoom' wallpaper mode.

    Returns (scaled_w, scaled_h, crop_x, crop_y, scale).
    """
    scale = max(target_w / img_w, target_h / img_h)
    scaled_w = round(img_w * scale)
    scaled_h = round(img_h * scale)
    crop_x = (scaled_w - target_w) // 2
    crop_y = (scaled_h - target_h) // 2
    return scaled_w, scaled_h, crop_x, crop_y, scale


def _axis_map(src_w: int, src_h: int, target_w: int, target_h: int):
    """Per-axis (scale, crop) of the real zoom-resize.

    Both axes are needed: in zoom mode one of them decides the scale and the
    other is cropped, and which one depends on the source's aspect ratio.
    The scale is the one actually applied (rounded size / source size).
    """
    scaled_w, scaled_h, crop_x, crop_y, _ = zoom_resize(src_w, src_h, target_w, target_h)
    return (scaled_w / src_w, crop_x), (scaled_h / src_h, crop_y)


def screen_to_source(
    screen_x: int, screen_y: int,
    src_w: int, src_h: int, target_w: int, target_h: int,
) -> tuple[int, int]:
    """Map a screen-space point back to source image coordinates.

    Inverts: source → scale → crop → screen, i.e.
    source = (screen + crop) / scale on each axis.
    """
    (sx, cx), (sy, cy) = _axis_map(src_w, src_h, target_w, target_h)
    return round((screen_x + cx) / sx), round((screen_y + cy) / sy)


def source_to_screen(
    source_x: int, source_y: int,
    src_w: int, src_h: int, target_w: int, target_h: int,
) -> tuple[int, int]:
    """Map a source image point to screen-space coordinates."""
    (sx, cx), (sy, cy) = _axis_map(src_w, src_h, target_w, target_h)
    return round(source_x * sx - cx), round(source_y * sy - cy)


def apply_effect(
    input_path: str,
    output_path: str,
    ir: DockPromptIR,
) -> dict:
    """Deterministically resize + apply effect to the dock region.

    The dock coordinates in the IR are in FINAL CANVAS coords (screen space).
    We resize the image to match the canvas, then apply the effect directly
    at those screen coordinates. No mapping needed — they're already correct.

    Returns a result dict with what was done.
    """
    from PIL import Image, ImageFilter

    target_w = ir.display.width
    target_h = ir.display.height

    img = Image.open(input_path)
    src_w, src_h = img.size

    # Step 1: Zoom-resize to exact canvas (matches GNOME)
    scaled_w, scaled_h, crop_x, crop_y, scale = zoom_resize(
        src_w, src_h, target_w, target_h
    )
    img = img.resize((scaled_w, scaled_h), Image.LANCZOS)
    img = img.crop((crop_x, crop_y, crop_x + target_w, crop_y + target_h))

    # Step 2: Dock coords are already in screen space — use directly
    dk = ir.dock
    fx, fy, fw, fh = dk.x, dk.y, dk.width, dk.height

    # Step 3: Apply effect inside the dock region
    if fw > 0 and fh > 0 and dk.edge != "none":
        effect = ir.intent.effect
        dock_box = (fx, fy, fx + fw, fy + fh)
        dock_region = img.crop(dock_box)

        if effect == "blur":
            dock_region = dock_region.filter(ImageFilter.GaussianBlur(radius=20))
        elif effect == "darken":
            from PIL import ImageEnhance
            dock_region = ImageEnhance.Brightness(dock_region).enhance(0.5)
        elif effect == "tint":
            # Blend toward a navy wash; light stays lighter than dark, so the
            # wallpaper under the dock is still recognisable.
            dock_region = dock_region.convert("RGB")
            wash = Image.new("RGB", dock_region.size, TINT_COLOR)
            dock_region = Image.blend(dock_region, wash, TINT_ALPHA)

        img.paste(dock_region, (fx, fy))

    # Step 4: Save exact canvas
    img.save(output_path, quality=95)

    # Where the dock WAS in the original source image (for reference)
    src_x0, src_y0 = screen_to_source(fx, fy, src_w, src_h, target_w, target_h)
    src_x1, src_y1 = screen_to_source(fx + fw, fy + fh, src_w, src_h, target_w, target_h)

    return {
        "input": input_path,
        "output": output_path,
        "source_size": f"{src_w}x{src_h}",
        "canvas_size": f"{target_w}x{target_h}",
        "scale": round(scale, 4),
        "crop_offset": f"{crop_x},{crop_y}",
        "dock_screen": f"x={fx} y={fy} w={fw} h={fh}",
        "dock_in_source": f"x={src_x0}..{src_x1} y={src_y0}..{src_y1}",
        "effect": ir.intent.effect,
    }
