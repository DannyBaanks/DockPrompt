# DockPrompt Chrome Extension

Paste your host geometry once, drop any image, get the exact `dockprompt apply` command.

## Install (developer mode)

1. Open `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this `chrome-extension/` folder

## Usage

1. Run `dockprompt inspect` on your Linux host
2. Paste the output into the "Host geometry" box (saves to localStorage)
3. Drop any image onto the drop zone
4. Pick effect (blur/darken/tint)
5. Copy the generated command and run it on your host

## Design

- **Glassmorphism** panels with backdrop blur
- **Step system** with animated badges (1→2→3→done)
- **Mini screen preview** showing dock position
- **Command tabs**: Apply, Prompt, Inspect
- **Terminal aesthetic**: green-on-black, dot bar, copy button
- **Zero permissions**, zero network, zero frameworks

## Files

```
manifest.json   — Manifest V3, no permissions
popup.html      — UI with full design system
popup.js        — Logic (geometry parsing, image handling, command gen)
icon*.png       — Icons
ROADMAP.md      — UI/UX improvement roadmap
```
