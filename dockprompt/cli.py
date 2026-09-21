import argparse
import json
import subprocess
import sys

from dockprompt.geometry.normalize import derive_dock_region
from dockprompt.host.x11 import inspect_host
from dockprompt.ir import DockPromptIR, ImageInfo, Intent
from dockprompt.prompt.materialize import materialize_prompt


def _try_clipboard(text: str) -> bool:
    for cmd in (
        ["xclip", "-selection", "clipboard"],
        ["wl-copy"],
        ["xsel", "--clipboard", "--input"],
    ):
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            p.communicate(input=text.encode(), timeout=5)
            if p.returncode == 0:
                return True
        except FileNotFoundError:
            continue
    return False


def main():
    parser = argparse.ArgumentParser(
        prog="dockprompt",
        description="DockPrompt — Linux desktop geometry to AI-ready prompt",
    )
    parser.add_argument("image", nargs="?", help="Path to wallpaper image")
    parser.add_argument("effect_positional", nargs="?", help="Effect (positional)")
    parser.add_argument("--effect", dest="effect_flag", help="Effect: blur, darken, tint, custom")
    parser.add_argument("--json", action="store_true", help="Output IR as JSON")
    parser.add_argument("--copy", action="store_true", help="Copy prompt to clipboard")
    args = parser.parse_args()

    effect = args.effect_flag or args.effect_positional

    display, workarea, de, session = inspect_host()
    dock = derive_dock_region(display, workarea)

    image_info = ImageInfo()
    if args.image and args.image not in ("inspect",):
        try:
            from dockprompt.image.metadata import inspect_image
            image_info = inspect_image(args.image)
        except Exception:
            pass

    intent = Intent(effect=effect or "blur")
    ir = DockPromptIR(
        display=display, workarea=workarea, dock=dock,
        image=image_info, intent=intent,
    )

    is_inspect = (
        args.image == "inspect"
        or (args.image and not effect and not args.json and not args.copy)
    )

    if is_inspect:
        print("DockPrompt")
        print()
        print(f"Session: {session}")
        print(f"Desktop: {de}")
        print(f"Display: {display.width}x{display.height}")
        print(f"Workarea: {workarea.x},{workarea.y} {workarea.width}x{workarea.height}")
        print(f"Dock: {dock.edge}")
        if dock.edge != "none":
            print(f"Dock region: x={dock.x} y={dock.y} w={dock.width} h={dock.height}")
        if image_info.width:
            print(f"Image: {image_info.width}x{image_info.height}")
        print()
        print("Geometry: VERIFIED")
        return

    if args.json:
        print(json.dumps(ir.to_dict(), indent=2))
    else:
        print(materialize_prompt(ir))

    if args.copy:
        text = json.dumps(ir.to_dict(), indent=2) if args.json else materialize_prompt(ir)
        if _try_clipboard(text):
            print("[copied to clipboard]", file=sys.stderr)
        else:
            print("[no clipboard tool found — install xclip, wl-copy, or xsel]", file=sys.stderr)


if __name__ == "__main__":
    main()
