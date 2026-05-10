from dataclasses import dataclass

import numpy as np

from geometry_visualizer.types import PointsArray

APP_TITLE = "Geometry Transform Visualizer"
WINDOW_SIZE = "1100x700"
MIN_WINDOW_SIZE = (900, 600)

CANVAS_SCALE = 45.0
MIN_CANVAS_SCALE = 5.0
CAMERA_PADDING = 2.0

GRID_TARGET_PIXELS = 70
GRID_STEP_OPTIONS = (1, 2, 5, 10)
FLOAT_EPS = 1e-9

MAX_INPUT_ABS_VALUE = 1_000_000.0
MIN_SCALE_FACTOR = 1e-9

PANEL_WIDTH = 300
MOUSE_VERTEX_SELECTION_RADIUS = 14

COLOR_AXIS = "#222222"
COLOR_GRID = "#d0d0d0"
COLOR_GRID_LABEL = "#555555"

COLOR_CURRENT_OUTLINE = "#1f6aa5"
COLOR_CURRENT_VERTEX = "#3b8ed0"

COLOR_BACKGROUND_OUTLINE = "#777777"
COLOR_BACKGROUND_VERTEX = "#aaaaaa"

TEXT_HISTORY_INITIAL = "0: Исходная"
TEXT_NO_PREVIOUS_FIGURE = "Предыдущей фигуры пока нет."
TEXT_VERTEX_DRAGGED = "Вершина перемещена."

INITIAL_POINTS = np.array(
    [
        [-3.0, -1.0],
        [-1.0, 2.0],
        [2.0, 1.5],
        [3.0, -1.5],
    ],
    dtype=float,
)


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    title: str
    window_size: str
    min_window_size: tuple[int, int]
    initial_points: PointsArray

    @classmethod
    def default(cls) -> "AppConfig":
        """Create default application configuration."""
        return cls(
            title=APP_TITLE,
            window_size=WINDOW_SIZE,
            min_window_size=MIN_WINDOW_SIZE,
            initial_points=INITIAL_POINTS.copy(),
        )