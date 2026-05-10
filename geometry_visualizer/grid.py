import math

from geometry_visualizer.config import (
    FLOAT_EPS,
    GRID_STEP_OPTIONS,
    GRID_TARGET_PIXELS,
    MIN_CANVAS_SCALE,
)


def format_number(value: float) -> str:
    """Format coordinate value for displaying on the grid."""
    if abs(value) < FLOAT_EPS:
        return "0"

    if abs(value - round(value)) < FLOAT_EPS:
        return str(int(round(value)))

    return f"{value:.2f}".rstrip("0").rstrip(".")


def calculate_grid_step(scale: float) -> float:
    """Calculate a convenient grid step for the current zoom level."""
    safe_scale = max(scale, MIN_CANVAS_SCALE)
    raw_step = GRID_TARGET_PIXELS / safe_scale

    power = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / power

    for step in GRID_STEP_OPTIONS:
        if normalized <= step:
            return step * power

    return GRID_STEP_OPTIONS[-1] * power