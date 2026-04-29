from dataclasses import dataclass

import numpy as np

from geometry_visualizer.types import PointsArray

APP_TITLE = "Geometry Transform Visualizer"
WINDOW_SIZE = "1100x700"
MIN_WINDOW_SIZE = (900, 600)

CANVAS_SCALE = 45.0
MIN_CANVAS_SCALE = 5.0
GRID_TARGET_PIXELS = 70

MAX_INPUT_ABS_VALUE = 1_000_000.0
MIN_SCALE_FACTOR = 1e-9

INITIAL_POINTS = np.array(
    [[-3.0, -1.0], [-1.0, 2.0], [2.0, 1.5], [3.0, -1.5]], dtype=float
)


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration.

    Attributes:
        title: Application window title.
        window_size: Initial window size in Tk format.
        min_window_size: Minimal allowed window size.
        initial_points: Initial polygon vertices.
    """

    title: str
    window_size: str
    min_window_size: tuple[int, int]
    initial_points: PointsArray

    @classmethod
    def default(cls) -> "AppConfig":
        """Create default application configuration.

        Returns:
            Default configuration object.
        """
        return cls(
            title=APP_TITLE,
            window_size=WINDOW_SIZE,
            min_window_size=MIN_WINDOW_SIZE,
            initial_points=INITIAL_POINTS.copy(),
        )
