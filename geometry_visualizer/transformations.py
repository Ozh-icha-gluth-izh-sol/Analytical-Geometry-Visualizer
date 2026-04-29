import math

import numpy as np

from geometry_visualizer.types import PointArray, PointsArray


def figure_center(points: PointsArray) -> PointArray:
    """Return the geometric center of a polygon.

    Args:
        points: Polygon vertices as an array.

    Returns:
        Center point.
    """
    return np.mean(points, axis=0)


def translate_points(points: PointsArray, dx: float, dy: float) -> PointsArray:
    """Translate points by the vector (dx, dy).

    Args:
        points: Polygon vertices as an array.
        dx: Shift along the x-axis.
        dy: Shift along the y-axis.

    Returns:
        New array of translated points.
    """
    vector = np.array([dx, dy], dtype=float)
    return points + vector


def rotate_points(
    points: PointsArray, angle_degrees: float, center: PointArray
) -> PointsArray:
    """Rotate points around the given center.

    Args:
        points: Polygon vertices as an array.
        angle_degrees: Rotation angle in degrees.
        center: Rotation center as an array.

    Returns:
        New array of rotated points.
    """
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
    points: PointsArray, sx: float, sy: float, center: PointArray
) -> PointsArray:
    """Scale points relative to the given center.

    Args:
        points: Polygon vertices as an array.
        sx: Scale coefficient along the x-axis.
        sy: Scale coefficient along the y-axis.
        center: Scaling center as an array.

    Returns:
        New array of scaled points.
    """
    scale_matrix = np.array([[sx, 0.0], [0.0, sy]], dtype=float)

    return (points - center) @ scale_matrix.T + center
