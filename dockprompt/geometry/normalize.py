from dockprompt.ir import DisplayGeometry, Workarea, DockRegion


def derive_dock_region(display: DisplayGeometry, workarea: Workarea) -> DockRegion:
    """Derive dock region from display dims and workarea.

    ALL coordinates are final canvas coordinates (target display resolution).
    """
    if workarea.width <= 0 or workarea.height <= 0:
        return DockRegion(edge="none")

    wx = max(0, min(workarea.x, display.width))
    wy = max(0, min(workarea.y, display.height))
    ww = max(0, min(workarea.width, display.width - wx))
    wh = max(0, min(workarea.height, display.height - wy))

    top = wy
    bottom = display.height - wy - wh
    left = wx
    right = display.width - wx - ww

    reserved = {"top": top, "bottom": bottom, "left": left, "right": right}
    edge = max(reserved, key=reserved.get)

    if reserved[edge] <= 0:
        return DockRegion(edge="none")

    if edge == "bottom":
        return DockRegion(
            edge="bottom", x=0,
            y=display.height - bottom,
            width=display.width, height=bottom,
        )
    elif edge == "top":
        return DockRegion(
            edge="top", x=0, y=0,
            width=display.width, height=top,
        )
    elif edge == "left":
        return DockRegion(
            edge="left", x=0, y=0,
            width=left, height=display.height,
        )
    elif edge == "right":
        return DockRegion(
            edge="right",
            x=display.width - right, y=0,
            width=right, height=display.height,
        )

    return DockRegion(edge="none")
