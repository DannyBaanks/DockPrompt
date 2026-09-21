from dockprompt.ir import (
    DisplayGeometry, DockPromptIR, DockRegion, ImageInfo, Intent, Workarea,
)
from dockprompt.prompt.materialize import materialize_prompt


def test_blur_bottom_dock_contains_54():
    ir = DockPromptIR(
        display=DisplayGeometry(1920, 1080),
        workarea=Workarea(0, 32, 1920, 994),
        dock=DockRegion(edge="bottom", x=0, y=1026, width=1920, height=54),
        image=ImageInfo(3840, 2160, "JPEG", "1.7778"),
        intent=Intent(effect="blur"),
    )
    prompt = materialize_prompt(ir)
    assert "54" in prompt
    # "1080" contains "108" as substring — check the dock height specifically
    assert "height=54" in prompt
    assert "height=108" not in prompt
    assert "wallpaper source, not a screenshot" in prompt
    assert "1920×1080" in prompt


def test_blur_prompt_mentions_effect():
    ir = DockPromptIR(
        display=DisplayGeometry(1920, 1080),
        workarea=Workarea(0, 32, 1920, 994),
        dock=DockRegion(edge="bottom", x=0, y=1026, width=1920, height=54),
        intent=Intent(effect="darken"),
    )
    prompt = materialize_prompt(ir)
    assert "darken" in prompt


def test_no_dock_prompt():
    ir = DockPromptIR(
        display=DisplayGeometry(1920, 1080),
        workarea=Workarea(0, 0, 1920, 1080),
        dock=DockRegion(edge="none"),
        intent=Intent(effect="blur"),
    )
    prompt = materialize_prompt(ir)
    assert "No dock region" in prompt
