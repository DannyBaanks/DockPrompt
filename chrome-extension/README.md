# DockPrompt browser extension

A small local-only companion for the DockPrompt CLI.

It does three things:

1. Paste the output of `dockprompt inspect`.
2. Drop a wallpaper to read its dimensions locally.
3. Generate either an exact AI editing prompt, an `apply` command, or the host `inspect` command.

## Privacy

The extension has **no network permissions** and uploads nothing. Images are read only inside the popup with the browser `FileReader` API.

## Geometry is authoritative

The extension renders the dock preview from the exact `Dock region: x=… y=… w=… h=…` rectangle. Source-image resolution never changes the host dock coordinates.

Example:

```text
Display: 1920x1080
Workarea: 0,32 1920x994
Dock: bottom
Dock region: x=0 y=1026 w=1920 h=54
```

The generated AI prompt explicitly states that the dock is **54 px in the final 1920×1080 canvas**, even when the source wallpaper is 2×, 4K, or any other resolution.

## Load unpacked

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select this `chrome-extension/` directory.

No build step is required.
