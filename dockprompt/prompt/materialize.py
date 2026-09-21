from dockprompt.ir import DockPromptIR


def materialize_prompt(ir: DockPromptIR) -> str:
    d = ir.display
    dk = ir.dock
    intent = ir.intent

    lines = [
        "Edit the attached wallpaper for this Linux desktop.",
        "",
        f"The target display is exactly {d.width}×{d.height} pixels.",
    ]

    if dk.edge != "none":
        lines += [
            "",
            "The desktop dock occupies exactly this rectangle in target-display coordinates:",
            f"x={dk.x}",
            f"y={dk.y}",
            f"width={dk.width}",
            f"height={dk.height}",
            "",
            f"Apply the requested {intent.effect} effect only inside that rectangle.",
            "",
            "Preserve everything outside the specified dock region.",
            "Do not infer the dock size visually.",
            "Do not double dimensions because the source image has a different resolution.",
            f"All region coordinates refer to the FINAL {d.width}×{d.height} canvas.",
        ]
    else:
        lines += [
            "",
            "No dock region detected. Apply the effect to the full image.",
        ]

    lines += [
        "",
        "Do not add desktop UI, panels, icons, windows, text, taskbars or other interface elements.",
        "The supplied image is the wallpaper source, not a screenshot to recreate.",
        "",
        "Do not crop or recompose the image unless explicitly requested.",
        "If scaling is required to reach the target resolution, preserve the complete source composition.",
    ]

    if dk.edge != "none" and intent.effect == "blur":
        if dk.edge == "bottom":
            lines += [
                "",
                f"The blur boundary must begin exactly at y={dk.y} and extend through the final row.",
            ]
        elif dk.edge == "top":
            lines += [
                "",
                f"The blur boundary must begin at y=0 and extend through y={dk.height - 1}.",
            ]
        lines += [
            "No feathering or gradient outside the requested region.",
            "",
            "The isolated wallpaper may look unusual without the dock on top; "
            "exact alignment with the real Linux dock is the priority.",
        ]

    return "\n".join(lines)
