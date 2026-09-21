from dataclasses import dataclass, field, asdict


@dataclass
class DisplayGeometry:
    width: int = 0
    height: int = 0


@dataclass
class Workarea:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass
class DockRegion:
    edge: str = "none"
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass
class ImageInfo:
    width: int = 0
    height: int = 0
    format: str = "unknown"
    aspect_ratio: str = "unknown"


@dataclass
class Intent:
    effect: str = "blur"
    crop: bool = False
    preserve_outside_region: bool = True
    feather: bool = False


@dataclass
class DockPromptIR:
    display: DisplayGeometry = field(default_factory=DisplayGeometry)
    workarea: Workarea = field(default_factory=Workarea)
    dock: DockRegion = field(default_factory=DockRegion)
    image: ImageInfo = field(default_factory=ImageInfo)
    intent: Intent = field(default_factory=Intent)

    def to_dict(self) -> dict:
        return asdict(self)
