# Experiment 001: Before/After — Manual vs DockPrompt geometry

## Baseline (BEFORE)

- Human manually explained dock geometry to ChatGPT
- Model produced wrong region: 108px instead of 54px (2× source confusion)
- In another attempt, model modified a desktop screenshot instead of the wallpaper
- Human intent was correct, but geometry transmitted was ambiguous

## Classification

- host geometry discovery: DEMONSTRATED (manually, via xrandr + xprop)
- automatic DockPrompt discovery: NOT_DEMONSTRATED
- improved AI editing accuracy: NOT_DEMONSTRATED

## After (pending)

- dockprompt observes host → materializes prompt
- Danny passes prompt + wallpaper to ChatGPT
- Compare visual output against expected region
