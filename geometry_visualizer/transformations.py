import math

import numpy as np

from geometry_visualizer.types import PointArray, PointsArray


def figure_center(points: PointsArray) -> PointArray:
    """Return the geometric center of a polygon."""
    return np.mean(points, axis=0)


def translate_points(points: PointsArray, dx: float, dy: float) -> PointsArray:
    """Translate points by the vector ``(dx, dy)``."""
    vector = np.array([dx, dy], dtype=float)
    return points + vector


def rotate_points(
    points: PointsArray,
    angle_degrees: float,
    center: PointArray,
) -> PointsArray:
    """Rotate points around the given center."""
    radians = math.radians(angle_degrees)

    rotation_matrix = np.array(
        [
            [math.cos(radians), -math.sin(radians)],
            [math.sin(radians), math.cos(radians)],
        ],
        dtype=float,
    )

    return (points - center) @ rotation_matrix.T + center


def scale_points(
    points: PointsArray,
    sx: float,
    sy: float,
    center: PointArray,
) -> PointsArray:
    """Scale points relative to the given center."""
    scale_matrix = np.array(
        [
            [sx, 0.0],
            [0.0, sy],
        ],
        dtype=float,
    )

    return (points - center) @ scale_matrix.T + center


def reflect_x_axis(points: PointsArray) -> PointsArray:
    """Reflect points relative to the x-axis."""
    reflected = points.copy()
    reflected[:, 1] *= -1
    return reflected


def reflect_y_axis(points: PointsArray) -> PointsArray:
    """Reflect points relative to the y-axis."""
    reflected = points.copy()
    reflected[:, 0] *= -1
    return reflected