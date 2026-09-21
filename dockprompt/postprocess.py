"""Deterministic post-processor: resize + apply effect to exact canvas coords."""
from pathlib import Path

from dockprompt.ir import DockPromptIR, DockRegion, DisplayGeometry


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


def screen_to_source_y(
    screen_y: int,
    src_h: int, target_h: int,
) -> int:
    """Map a screen-space y coordinate back to source image y.

    Inverts: source → scale → crop → screen.
    screen_y = source_y * scale - crop_y
    source_y = (screen_y + crop_y) / scale
    """
    _, _, _, crop_y, scale = zoom_resize(1, src_h, 1, target_h)
    return round((screen_y + crop_y) / scale)


def source_to_screen_y(
    source_y: int,
    src_h: int, target_h: int,
) -> int:
    """Map a source image y coordinate to screen-space y."""
    _, _, _, crop_y, scale = zoom_resize(1, src_h, 1, target_h)
    return round(source_y * scale - crop_y)


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
            from PIL import ImageEnhance, ImageOps
            dock_region = ImageOps.colorize(
                dock_region.convert("L"), "#000044", "#000000"
            )
            dock_region = dock_region.convert("RGB")

        img.paste(dock_region, (fx, fy))

    # Step 4: Save exact canvas
    img.save(output_path, quality=95)

    # Where the dock WAS in the original source image (for reference)
    src_dock_y_top = screen_to_source_y(fy, src_h, target_h)
    src_dock_y_bot = screen_to_source_y(fy + fh, src_h, target_h)

    return {
        "input": input_path,
        "output": output_path,
        "source_size": f"{src_w}x{src_h}",
        "canvas_size": f"{target_w}x{target_h}",
        "scale": round(scale, 4),
        "crop_offset": f"{crop_x},{crop_y}",
        "dock_screen": f"x={fx} y={fy} w={fw} h={fh}",
        "dock_in_source": f"y={src_dock_y_top}..{src_dock_y_bot}",
        "effect": ir.intent.effect,
    }
