# DockPrompt

**Your Linux desktop already knows where your dock is. Why should you measure it?**

DockPrompt turns the geometry of your actual Linux desktop into an AI-ready image-editing prompt.

## What it does

When you want to edit your wallpaper (e.g., blur the dock area) using an AI model like ChatGPT, you need to tell it exact pixel coordinates. Getting those coordinates wrong is easy — a 2× scaling mismatch gives you 108px instead of 54px, and the result looks broken.

DockPrompt automates this:

1. **Inspects** your actual desktop (screen size, workarea, dock position)
2. **Computes** the exact dock rectangle in final canvas coordinates
3. **Materializes** an unambiguous prompt that tells the AI exactly what to do

It never edits your image. It never calls any API. It just produces the right prompt.

## Install

```bash
pip install .
# or with image metadata support:
pip install ".[image]"
```

## Usage

```bash
# See what DockPrompt detects about your desktop
dockprompt inspect

# See host + image info
dockprompt inspect wallpaper.jpg

# Generate a prompt for AI image editing
dockprompt wallpaper.jpg --effect blur

# Output as JSON (for piping)
dockprompt wallpaper.jpg --effect blur --json

# Copy prompt to clipboard
dockprompt wallpaper.jpg --effect blur --copy
```

## How it works

DockPrompt reads your X11 session data:
- `xrandr` for screen resolution
- `xprop -root _NET_WORKAREA` for the usable work area

From these two measurements, it computes where your dock sits and generates a prompt with exact pixel coordinates in the **final canvas** — never in source image coordinates.

## Supported effects

- `blur` — blur the dock region
- `darken` — darken the dock region
- `tint` — tint the dock region
- `custom` — custom text intent with geometry constraints

## Requirements

- Linux with X11 (GNOME/Ubuntu Dock)
- Python 3.10+
- Optional: Pillow for image metadata, xclip/wl-copy for clipboard

## License

MIT
