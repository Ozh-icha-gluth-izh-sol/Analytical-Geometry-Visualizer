import numpy as np
import pytest

from geometry_visualizer.transformations import (
    figure_center,
    reflect_x_axis,
    reflect_y_axis,
    rotate_points,
    scale_points,
    translate_points,
)


def test_figure_center_returns_mean_point() -> None:
    points = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]])
    result = figure_center(points)
    np.testing.assert_allclose(result, np.array([1.0, 1.0]))


def test_translate_points_moves_all_vertices() -> None:
    points = np.array([[1.0, 2.0], [3.0, 4.0]])

    result = translate_points(points, dx=10.0, dy=-2.0)
    expected = np.array([[11.0, 0.0], [13.0, 2.0]])

    np.testing.assert_allclose(result, expected)


def test_rotate_points_90_degrees_around_origin() -> None:
    points = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]])

    result = rotate_points(points, angle_degrees=90.0, center=np.array([0.0, 0.0]))
    expected = np.array([[0.0, 1.0], [-1.0, 0.0], [0.0, -1.0], [1.0, 0.0]])

    np.testing.assert_allclose(result, expected, atol=1e-9)


def test_scale_points_relative_to_center() -> None:
    points = np.array([[2.0, 1.0], [1.0, 2.0]])

    result = scale_points(points, sx=2.0, sy=3.0, center=np.array([1.0, 1.0]))
    expected = np.array([[3.0, 1.0], [1.0, 4.0]])

    np.testing.assert_allclose(result, expected)


@pytest.mark.parametrize(("points", "expected"), [(np.array([[1.0, 2.0], [-3.0, -4.0]]), np.array([[1.0, -2.0], [-3.0, 4.0]]))])

def test_reflect_x_axis(points: np.ndarray, expected: np.ndarray) -> None:
    result = reflect_x_axis(points)

    np.testing.assert_allclose(result, expected)


@pytest.mark.parametrize(("points", "expected"), [(np.array([[1.0, 2.0], [-3.0, -4.0]]), np.array([[-1.0, 2.0], [3.0, -4.0]]))])

def test_reflect_y_axis(points: np.ndarray, expected: np.ndarray) -> None:
    result = reflect_y_axis(points)

    np.testing.assert_allclose(result, expected)
