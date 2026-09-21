import argparse
import json
import subprocess
import sys
from pathlib import Path

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


def _build_ir(effect: str, image_path: str | None = None) -> DockPromptIR:
    display, workarea, de, session = inspect_host()
    dock = derive_dock_region(display, workarea)
    image_info = ImageInfo()
    if image_path:
        try:
            from dockprompt.image.metadata import inspect_image
            image_info = inspect_image(image_path)
        except Exception:
            pass
    return DockPromptIR(
        display=display, workarea=workarea, dock=dock,
        image=image_info, intent=Intent(effect=effect),
    )


def main():
    parser = argparse.ArgumentParser(
        prog="dockprompt",
        description="DockPrompt — Linux desktop geometry to AI-ready prompt",
    )
    sub = parser.add_subparsers(dest="command")

    # inspect
    p_inspect = sub.add_parser("inspect", help="Show detected host geometry")
    p_inspect.add_argument("image", nargs="?", help="Also show image info")

    # prompt (default behavior when no subcommand)
    parser.add_argument("image", nargs="?", help="Path to wallpaper image")
    parser.add_argument("effect_positional", nargs="?", help="Effect (positional)")
    parser.add_argument("--effect", dest="effect_flag", help="Effect: blur, darken, tint, custom")
    parser.add_argument("--json", action="store_true", help="Output IR as JSON")
    parser.add_argument("--copy", action="store_true", help="Copy prompt to clipboard")

    # apply
    p_apply = sub.add_parser("apply", help="Deterministically resize + apply effect")
    p_apply.add_argument("generated", help="Path to AI-generated image")
    p_apply.add_argument("--effect", dest="apply_effect", default="blur",
                         help="Effect: blur, darken, tint")
    p_apply.add_argument("-o", "--output", help="Output path (default: <input>_final.png)")

    args = parser.parse_args()

    # ── apply subcommand ──
    if args.command == "apply":
        ir = _build_ir(args.apply_effect)
        output = args.output
        if not output:
            stem = Path(args.generated).stem
            output = str(Path(args.generated).parent / f"{stem}_final.png")

        from dockprompt.postprocess import apply_effect
        result = apply_effect(args.generated, output, ir)

        print("DockPrompt Apply")
        print()
        print(f"Source image:  {result['source_size']}")
        print(f"Canvas:        {result['canvas_size']}")
        print(f"Scale factor:  {result['scale']}")
        print(f"Crop offset:   {result['crop_offset']}")
        print(f"Dock screen:   {result['dock_screen']}")
        print(f"Dock in source:{result['dock_in_source']}")
        print(f"Effect:        {result['effect']}")
        print(f"Output:        {result['output']}")
        return

    # ── inspect subcommand ──
    if args.command == "inspect":
        ir = _build_ir("blur", args.image)
        dk = ir.dock
        print("DockPrompt")
        print()
        print(f"Session: {inspect_host()[3]}")
        print(f"Desktop: {inspect_host()[2]}")
        print(f"Display: {ir.display.width}x{ir.display.height}")
        print(f"Workarea: {ir.workarea.x},{ir.workarea.y} {ir.workarea.width}x{ir.workarea.height}")
        print(f"Dock: {dk.edge}")
        if dk.edge != "none":
            print(f"Dock region: x={dk.x} y={dk.y} w={dk.width} h={dk.height}")
        if ir.image.width:
            print(f"Image: {ir.image.width}x{ir.image.height}")
        print()
        print("Geometry: VERIFIED")
        return

    # ── default: prompt mode ──
    effect = args.effect_flag or args.effect_positional
    ir = _build_ir(effect or "blur", args.image)

    is_inspect = (
        args.image == "inspect"
        or (args.image and not effect and not args.json and not args.copy)
    )

    if is_inspect:
        dk = ir.dock
        print("DockPrompt")
        print()
        print(f"Session: {inspect_host()[3]}")
        print(f"Desktop: {inspect_host()[2]}")
        print(f"Display: {ir.display.width}x{ir.display.height}")
        print(f"Workarea: {ir.workarea.x},{ir.workarea.y} {ir.workarea.width}x{ir.workarea.height}")
        print(f"Dock: {dk.edge}")
        if dk.edge != "none":
            print(f"Dock region: x={dk.x} y={dk.y} w={dk.width} h={dk.height}")
        if ir.image.width:
            print(f"Image: {ir.image.width}x{ir.image.height}")
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
