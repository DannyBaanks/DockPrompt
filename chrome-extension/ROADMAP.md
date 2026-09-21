# DockPrompt Chrome Extension — UI/UX Roadmap

## Current state
Functional popup: paste geometry, drop image, get command. Dark theme, monospace.
Works. Ugly. No soul.

## Vision
**The extension that makes you feel like a hacker from a movie, but one who actually knows what they're doing.**

Compact, fast, beautiful. Zero friction. One look and you understand everything.

---

## Phase 1: Visual foundation
*Make it look like it was designed, not assembled.*

### 1.1 Design system
- Color palette: deep navy bg (#0a0e1a), electric blue accents (#3b82f6), soft glow
- Typography: Inter for UI, JetBrains Mono for code/commands
- Spacing: 4/8/12/16/24px scale
- Border radius: 12px containers, 8px inputs, 6px buttons
- Subtle shadows with blue tint for depth

### 1.2 Container redesign
- Glassmorphism panels (backdrop-blur + semi-transparent bg)
- Subtle gradient border on active sections
- Smooth section transitions (height animated)
- Step numbers as glowing badges: 1 2 3 4

### 1.3 Header
- Logo with subtle pulse animation
- Version badge
- "New" badge when geometry hasn't been set

---

## Phase 2: Geometry input UX
*Make pasting geometry feel effortless.*

### 2.1 Smart paste
- Auto-detect `dockprompt inspect` output on paste
- Visual confirmation: green checkmark + mini screen preview
- Highlight parsed values with labels
- Error state: red border + "couldn't parse" + example

### 2.2 Geometry preview
- Mini screen visualization (16:9 rectangle)
- Dock region highlighted in electric blue
- Workarea shown in subtle gray
- Labels: "1920x1080", "dock: 54px"
- Animated on first load

### 2.3 Persistent state
- Geometry saved in localStorage
- Show "Last updated: 2 min ago"
- One-click "Clear and re-paste"
- Multiple geometry profiles (work/home)

---

## Phase 3: Image drop zone
*The drop zone should feel alive.*

### 3.1 Drop zone redesign
- Dashed border that animates on drag (dash to solid, color shift)
- Floating icon that bounces gently when idle
- On dragover: icon scales up, border glows, background pulses
- On drop: satisfying "snap" animation + checkmark

### 3.2 Image preview
- Rounded thumbnail with shadow
- Resolution badge overlay: "3840x2400"
- Filename truncated with ellipsis
- "x" button to remove and drop new one
- Side-by-side: original vs final canvas preview

### 3.3 Canvas preview
- Mini visualization: image scaled to 1920x1080
- Dock region overlay in semi-transparent blue
- Coordinates shown on hover
- Before/after toggle (original to blurred)

---

## Phase 4: Command generation
*The command should feel like the hero of the story.*

### 4.1 Command box redesign
- Syntax-highlighted terminal look
- Comment line in gray, command in green
- Typewriter animation on generation
- Copy button with ripple effect + "Copied!" toast
- QR code option for mobile copy

### 4.2 Command variations
- Tab bar: "Apply" | "Prompt" | "Inspect"
- Apply tab: `dockprompt apply ...`
- Prompt tab: the full prompt for ChatGPT
- Inspect tab: `dockprompt inspect`
- Each tab has its own copy button

### 4.3 One-click workflow
- "Copy + Open Terminal" button (if possible)
- "Download script" button (creates .sh file)
- "Share" button (copies command + geometry as formatted text)

---

## Phase 5: Onboarding and polish
*First impression matters.*

### 5.1 First-run experience
- Welcome screen: "Your Linux desktop has a secret. Let's find it."
- 3-step illustration: Paste, Drop, Apply
- "Get started" button auto-focuses geometry textarea
- Skip option (shows blank state with hint)

### 5.2 Empty states
- No geometry: screen icon with "?" + "Run dockprompt inspect"
- No image: cloud icon with "Drop an image here"
- No command: subtle "Complete the steps above"

### 5.3 Animations
- Section entrance: slide up + fade in
- Command generation: typing effect
- Copy success: confetti burst (tiny, tasteful)
- Error states: gentle shake

### 5.4 Keyboard shortcuts
- Ctrl+V in geometry box: auto-parse
- Ctrl+V anywhere: paste image if clipboard has one
- Ctrl+C when command visible: copy command
- Esc: close popup

---

## Phase 6: Advanced features
*Power user territory.*

### 6.1 Custom dock regions
- Manual coordinate input (non-standard setups)
- "I don't have a dock" option
- Multiple dock regions (top panel + bottom dock)

### 6.2 Batch mode
- Drop multiple images
- Generate script that processes all of them
- Progress indicator

### 6.3 Export formats
- Shell command
- Python script
- JSON config for dockprompt
- Bash script with error handling

---

## Priority order

| Phase | Impact | Effort | Do first? |
|-------|--------|--------|-----------|
| 1. Visual foundation | HIGH | LOW | YES |
| 2. Geometry input | HIGH | MEDIUM | YES |
| 3. Image drop | HIGH | MEDIUM | YES |
| 4. Command generation | HIGH | LOW | YES |
| 5. Onboarding | MEDIUM | MEDIUM | LATER |
| 6. Advanced | LOW | HIGH | MUCH LATER |

**Start with Phase 1 + 2 + 3 + 4 in parallel.**
That gives you a beautiful, functional extension.
Phases 5 and 6 are polish.

---

## Tech notes

- **No frameworks.** Pure HTML/CSS/JS. Tiny and fast.
- **CSS variables** for the design system (easy to tweak).
- **requestAnimationFrame** for smooth animations.
- **localStorage** for state persistence.
- **Clipboard API** for copy (with fallback).
- **FileReader API** for image preview.
- **No external dependencies.** Zero CDN calls.

---

## Inspiration

- Raycast (macOS launcher) — clean, fast, keyboard-first
- Linear — beautiful dark UI, subtle animations
- Vercel — minimal, confident design
- GitHub Copilot CLI — terminal aesthetic, green-on-black
