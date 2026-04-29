import math
import tkinter as tk
from typing import Any, Protocol

import numpy as np

from geometry_visualizer.config import (
    CANVAS_SCALE,
    GRID_TARGET_PIXELS,
    MIN_CANVAS_SCALE,
)
from geometry_visualizer.types import PointArray, PointsArray


class CanvasAppProtocol(Protocol):
    """Protocol describing data required by GeometryCanvas."""

    original_points: PointsArray
    current_points: PointsArray


class GeometryCanvas(tk.Canvas):
    """Canvas for rendering a coordinate plane and geometric figures."""

    def __init__(
        self,
        master: tk.Misc,
        app: CanvasAppProtocol,
        **kwargs: Any,
    ) -> None:
        """Initialize the canvas.

        Args:
            master: Parent Tk widget.
            app: Application object that stores original and current points.
            **kwargs: Additional Tk Canvas options.
        """
        super().__init__(master, **kwargs)

        self.app = app
        self.scale = CANVAS_SCALE
        self.view_center = np.array([0.0, 0.0], dtype=float)

        self.bind("<Configure>", lambda event: self.redraw())

    @staticmethod
    def format_number(value: float) -> str:
        """Format coordinate value for displaying on the grid.

        Args:
            value: Numeric coordinate value.

        Returns:
            Short string representation of the coordinate.
        """
        if abs(value) < 1e-9:
            return "0"

        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))

        return f"{value:.2f}".rstrip("0").rstrip(".")

    def get_grid_step(self) -> float:
        """Calculate a convenient grid step for the current zoom level.

        Returns:
            Grid step in world coordinates.
        """
        raw_step = GRID_TARGET_PIXELS / self.scale
        power = 10 ** math.floor(math.log10(raw_step))
        normalized = raw_step / power

        if normalized <= 1:
            step = 1
        elif normalized <= 2:
            step = 2
        elif normalized <= 5:
            step = 5
        else:
            step = 10

        return step * power

    def world_to_screen(
        self, point: PointArray | tuple[float, float]
    ) -> tuple[float, float]:
        """Convert world coordinates to screen coordinates.

        Args:
            point: Point in mathematical coordinates.

        Returns:
            Point in canvas screen coordinates.
        """
        x, y = point

        width = self.winfo_width()
        height = self.winfo_height()

        screen_x = width / 2 + (x - self.view_center[0]) * self.scale
        screen_y = height / 2 - (y - self.view_center[1]) * self.scale

        return screen_x, screen_y

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates.

        Args:
            sx: Screen x-coordinate.
            sy: Screen y-coordinate.

        Returns:
            Point in mathematical coordinates.
        """
        width = self.winfo_width()
        height = self.winfo_height()

        x = self.view_center[0] + (sx - width / 2) / self.scale
        y = self.view_center[1] - (sy - height / 2) / self.scale

        return x, y

    def fit_to_points(self, points: PointsArray, padding: float = 2.0) -> None:
        """Move camera and adjust zoom so points fit into the canvas.

        Args:
            points: Points that should be visible.
            padding: Extra empty space around the points in world coordinates.
        """
        if len(points) == 0:
            return

        points = np.array(points, dtype=float)

        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        min_x = np.min(points[:, 0])
        max_x = np.max(points[:, 0])
        min_y = np.min(points[:, 1])
        max_y = np.max(points[:, 1])

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.view_center = np.array([center_x, center_y], dtype=float)

        world_width = max(max_x - min_x, 1.0) + 2 * padding
        world_height = max(max_y - min_y, 1.0) + 2 * padding

        scale_x = width / world_width
        scale_y = height / world_height

        self.scale = max(MIN_CANVAS_SCALE, min(scale_x, scale_y))

    def draw_grid(self) -> None:
        """Draw coordinate grid and coordinate axes."""
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        self.delete("grid")

        step = self.get_grid_step()

        left_world, top_world = self.screen_to_world(0, 0)
        right_world, bottom_world = self.screen_to_world(width, height)

        x_min = math.floor(left_world / step) * step
        x_max = math.ceil(right_world / step) * step

        y_min = math.floor(bottom_world / step) * step
        y_max = math.ceil(top_world / step) * step

        axis_x_screen, axis_y_screen = self.world_to_screen((0, 0))

        x = x_min
        while x <= x_max + step / 2:
            sx, _ = self.world_to_screen((x, 0))

            is_axis = abs(x) < 1e-9
            color = "#222222" if is_axis else "#d0d0d0"
            line_width = 2 if is_axis else 1

            self.create_line(
                sx,
                0,
                sx,
                height,
                fill=color,
                width=line_width,
                tags="grid",
            )

            if not is_axis:
                if 0 <= axis_y_screen <= height:
                    label_y = axis_y_screen + 14
                else:
                    label_y = height - 15

                self.create_text(
                    sx + 10,
                    label_y,
                    text=self.format_number(x),
                    fill="#555555",
                    font=("Arial", 10),
                    tags="grid",
                )

            x += step

        y = y_min
        while y <= y_max + step / 2:
            _, sy = self.world_to_screen((0, y))

            is_axis = abs(y) < 1e-9
            color = "#222222" if is_axis else "#d0d0d0"
            line_width = 2 if is_axis else 1

            self.create_line(
                0,
                sy,
                width,
                sy,
                fill=color,
                width=line_width,
                tags="grid",
            )

            if not is_axis:
                if 0 <= axis_x_screen <= width:
                    label_x = axis_x_screen + 18
                else:
                    label_x = 20

                self.create_text(
                    label_x,
                    sy - 10,
                    text=self.format_number(y),
                    fill="#555555",
                    font=("Arial", 10),
                    tags="grid",
                )

            y += step

        if 0 <= axis_y_screen <= height:
            self.create_text(
                width - 20,
                axis_y_screen - 15,
                text="x",
                fill="#222222",
                font=("Arial", 14, "bold"),
                tags="grid",
            )

        if 0 <= axis_x_screen <= width:
            self.create_text(
                axis_x_screen + 15,
                20,
                text="y",
                fill="#222222",
                font=("Arial", 14, "bold"),
                tags="grid",
            )

    def draw_polygon(
        self,
        points: PointsArray,
        outline: str,
        vertex_color: str,
        dash: tuple[int, int] | None = None,
        label_prefix: str = "",
    ) -> None:
        """Draw polygon edges, vertices and coordinate labels.

        Args:
            points: Polygon vertices.
            outline: Edge and text color.
            vertex_color: Vertex fill color.
            dash: Optional line dash pattern.
            label_prefix: Prefix for vertex labels.
        """
        if len(points) == 0:
            return

        screen_points = [self.world_to_screen(point) for point in points]

        if len(screen_points) >= 2:
            for i in range(len(screen_points)):
                x1, y1 = screen_points[i]
                x2, y2 = screen_points[(i + 1) % len(screen_points)]

                self.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=outline,
                    width=3,
                    dash=dash,
                    tags="figure",
                )

        for index, point in enumerate(points):
            x, y = self.world_to_screen(point)

            self.create_oval(
                x - 5,
                y - 5,
                x + 5,
                y + 5,
                fill=vertex_color,
                outline="black",
                tags="figure",
            )

            label_x = self.format_number(float(point[0]))
            label_y = self.format_number(float(point[1]))
            text = f"{label_prefix}{index + 1} ({label_x}; {label_y})"

            self.create_text(
                x + 45,
                y - 15,
                text=text,
                fill=outline,
                font=("Arial", 10, "bold"),
                tags="figure",
            )

    def redraw(self) -> None:
        """Clear the canvas and redraw the whole scene."""
        self.delete("all")

        self.draw_grid()

        self.draw_polygon(
            self.app.original_points,
            outline="#777777",
            vertex_color="#aaaaaa",
            dash=(5, 4),
            label_prefix="A",
        )

        self.draw_polygon(
            self.app.current_points,
            outline="#1f6aa5",
            vertex_color="#3b8ed0",
            dash=None,
            label_prefix="A'",
        )
