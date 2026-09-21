from dockprompt.ir import ImageInfo


def inspect_image(path: str) -> ImageInfo:
    try:
        from PIL import Image
        with Image.open(path) as img:
            w, h = img.size
            fmt = img.format or "unknown"
            ratio = f"{w / h:.4f}" if h else "unknown"
            return ImageInfo(width=w, height=h, format=fmt, aspect_ratio=ratio)
    except ImportError:
        pass
    except Exception:
        pass
    return ImageInfo()
