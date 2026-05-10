import math

from geometry_visualizer.grid import calculate_grid_step, format_number


def test_integer_without_decimal() -> None:
    assert format_number(2.0) == "2"


def test_zero_epsilon() -> None:
    assert format_number(1e-12) == "0"


def test_fraction() -> None:
    assert format_number(1.5) == "1.5"


def test_grid_step_positive() -> None:
    assert calculate_grid_step(45.0) > 0


def test_grid_step_readable() -> None:
    step = calculate_grid_step(45.0)

    power = 10 ** math.floor(math.log10(step))
    normalized = round(step / power)

    assert normalized in {1, 2, 5, 10}


def test_negative_integer() -> None:
    assert format_number(-5.0) == "-5"


def test_negative_fraction() -> None:
    assert format_number(-1.25) == "-1.25"


def test_trailing_zeroes_removed() -> None:
    assert format_number(1.50) == "1.5"


def test_rounds_to_two_digits() -> None:
    assert format_number(1.23456) == "1.23"


def test_step_grows_on_zoom_out() -> None:
    large_scale_step = calculate_grid_step(100.0)
    small_scale_step = calculate_grid_step(10.0)

    assert small_scale_step >= large_scale_step


def test_step_shrinks_on_zoom_in() -> None:
    small_scale_step = calculate_grid_step(10.0)
    large_scale_step = calculate_grid_step(100.0)

    assert large_scale_step <= small_scale_step


def test_tiny_scale_step_positive() -> None:
    assert calculate_grid_step(0.0001) > 0