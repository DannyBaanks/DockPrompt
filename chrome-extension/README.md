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

## How it works

- No background scripts, no content scripts, no network access
- No special permissions required
- Geometry stored in localStorage (never leaves your browser)
- Generates shell commands only — you run them yourself

## Files

```
manifest.json   — Manifest V3, no permissions
popup.html      — UI
popup.js        — logic (geometry parsing, command generation)
icon*.png       — icons
```
