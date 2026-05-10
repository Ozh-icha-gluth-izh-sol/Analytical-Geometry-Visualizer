from __future__ import annotations

import cProfile
import io
import pstats
import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_visualizer.grid import calculate_grid_step, format_number
from geometry_visualizer.transformations import (
    reflect_x_axis,
    reflect_y_axis,
    rotate_points,
    scale_points,
    translate_points,
)

REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORT_DIR / "profiling_report.md"

POINTS_COUNT = 10_000
REPEATS_FAST = 1_000
REPEATS_MEDIUM = 500
REPEATS_GRID = 100_000


def benchmark(name: str, func: Callable[..., Any], *args: Any, repeats: int) -> dict[str, float | str | int]:
    start = time.perf_counter()

    for _ in range(repeats):
        func(*args)

    total = time.perf_counter() - start

    return {
        "name": name,
        "repeats": repeats,
        "total_seconds": total,
        "average_ms": total / repeats * 1000,
    }


def run_workload(points: np.ndarray) -> None:
    center = np.array([0.0, 0.0], dtype=float)

    for _ in range(300):
        translate_points(points, 1.0, -1.0)
        rotate_points(points, 45.0, center)
        scale_points(points, 1.5, 0.8, center)
        reflect_x_axis(points)
        reflect_y_axis(points)

    for scale in range(5, 500):
        calculate_grid_step(float(scale))
        format_number(float(scale) / 3)


def get_profile_text(points: np.ndarray) -> str:
    profiler = cProfile.Profile()
    profiler.enable()

    run_workload(points)

    profiler.disable()

    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumtime").print_stats(25)

    return stream.getvalue()


def create_report(results: list[dict[str, float | str | int]], profile_text: str) -> str:
    rows = "\n".join("| {name} | {repeats} | {total_seconds} | {average_ms} |".format(**result) for result in results)

    slowest = max(results, key=lambda result: float(result["average_ms"]))

    return f"""# Profiling Report

Проверяем скорость работы основных функций на массиве из `{POINTS_COUNT}` точек.

## Benchmark

| Функция | Количество запусков | Общее время, сек | Среднее время, мс |
|---|---:|---:|---:|
{rows}

## Самая дорогая функция

```text
{slowest["name"]}: {float(slowest["average_ms"])} мс на вызов {profile_text}

"""

def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)

    rng = np.random.default_rng(seed=42)
    points = rng.normal(size=(POINTS_COUNT, 2))
    center = np.array([0.0, 0.0], dtype=float)

    results = [
        benchmark("translate_points", translate_points, points, 1.0, -1.0, repeats=REPEATS_FAST),
        benchmark("rotate_points", rotate_points, points, 45.0, center, repeats=REPEATS_MEDIUM),
        benchmark("scale_points", scale_points, points, 1.5, 0.8, center, repeats=REPEATS_MEDIUM),
        benchmark("reflect_x_axis", reflect_x_axis, points, repeats=REPEATS_FAST),
        benchmark("reflect_y_axis", reflect_y_axis, points, repeats=REPEATS_FAST),
        benchmark("calculate_grid_step", calculate_grid_step, 45.0, repeats=REPEATS_GRID),
        benchmark("format_number", format_number, 123.456, repeats=REPEATS_GRID),
    ]

    profile_text = get_profile_text(points)
    report_text = create_report(results, profile_text)
    REPORT_PATH.write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    main()