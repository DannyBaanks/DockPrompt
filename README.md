# DockPrompt

**Your Linux desktop already knows where your dock is. Why should you measure it?**

DockPrompt turns the geometry of your actual Linux desktop into an AI-ready image-editing prompt — and then applies the result deterministically.

## What it does

When you want to edit your wallpaper (e.g., blur the dock area) using an AI model like ChatGPT, two things go wrong:

1. **Coordinates get confused** — a 2× scaling mismatch gives you 108px instead of 54px
2. **The AI doesn't respect your canvas** — it generates whatever resolution it wants, and GNOME scales/crops it

DockPrompt solves both:

1. **Inspect** → detects your real desktop geometry (screen, workarea, dock)
2. **Prompt** → materializes exact coordinates in final canvas space
3. **Apply** → takes the AI output and deterministically resizes + applies the effect at pixel-perfect coordinates

## Install

```bash
pip install .
# or with image metadata support:
pip install ".[image]"
```

## Usage

### Step 1: Generate the prompt

```bash
# See what DockPrompt detects
dockprompt inspect

# Generate a prompt for ChatGPT
dockprompt wallpaper.jpg --effect blur

# Copy to clipboard
dockprompt wallpaper.jpg --effect blur --copy
```

### Step 2: Send to AI

Give the prompt + your wallpaper to ChatGPT (or any image model). Save the output.

### Step 3: Apply deterministically

```bash
# Resize to exact canvas + blur the dock region
dockprompt apply chatgpt_output.png

# Custom output path
dockprompt apply chatgpt_output.png -o final_wallpaper.png

# Different effect
dockprompt apply chatgpt_output.png --effect darken
```

`apply` does:
- Zoom-resizes to your exact screen resolution (matches GNOME's `zoom` mode)
- Maps the dock region through the same scaling
- Applies the effect only inside the dock rectangle
- Outputs a pixel-perfect canvas-ready image

## How it works

DockPrompt reads your X11 session data:
- `xrandr` for screen resolution
- `xprop -root _NET_WORKAREA` for the usable work area

From these two measurements, it computes where your dock sits. All coordinates are in **final canvas space** — the AI can generate any resolution, and `apply` will normalize it.

## Supported effects

- `blur` — blur the dock region
- `darken` — darken the dock region
- `tint` — tint the dock region

## Architecture

```
inspect → host geometry → IR → prompt materializer → AI
                                              ↓
                                        AI output image
                                              ↓
                                    apply → zoom-resize
                                          → map dock coords
                                          → deterministic effect
                                          → pixel-perfect output
```

## Requirements

- Linux with X11 (GNOME/Ubuntu Dock)
- Python 3.10+
- Pillow (for `apply` and image metadata)
- Optional: xclip/wl-copy for clipboard

## License

MIT
