import math
import tkinter as tk
from typing import Any

import numpy as np

from geometry_visualizer.config import (
    CAMERA_PADDING,
    CANVAS_SCALE,
    COLOR_AXIS,
    COLOR_BACKGROUND_OUTLINE,
    COLOR_BACKGROUND_VERTEX,
    COLOR_CURRENT_OUTLINE,
    COLOR_CURRENT_VERTEX,
    COLOR_GRID,
    COLOR_GRID_LABEL,
    FLOAT_EPS,
    MIN_CANVAS_SCALE,
    MOUSE_VERTEX_SELECTION_RADIUS,
)
from geometry_visualizer.grid import calculate_grid_step, format_number
from geometry_visualizer.types import PointArray, PointsArray


class GeometryCanvas(tk.Canvas):
    """Canvas for rendering a coordinate plane and geometric figures."""

    VERTEX_RADIUS = 5
    POLYGON_LINE_WIDTH = 3
    AXIS_LINE_WIDTH = 2
    GRID_LINE_WIDTH = 1

    GRID_FONT = ("Arial", 10)
    AXIS_FONT = ("Arial", 14, "bold")
    VERTEX_FONT = ("Arial", 10, "bold")

    def __init__(
        self,
        master: tk.Misc,
        app: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the canvas."""
        super().__init__(master, **kwargs)

        self.app = app
        self.scale = CANVAS_SCALE
        self.view_center = np.array([0.0, 0.0], dtype=float)
        self.selected_vertex_index: int | None = None

        self.bind("<Configure>", lambda event: self.redraw())
        self.bind("<ButtonPress-1>", self._on_mouse_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_release)

    @staticmethod
    def is_axis(value: float) -> bool:
        """Check whether coordinate value belongs to an axis."""
        return abs(value) < FLOAT_EPS

    def world_to_screen(
        self,
        point: PointArray | tuple[float, float],
    ) -> tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        x, y = point

        width = self.winfo_width()
        height = self.winfo_height()

        screen_x = width / 2 + (x - self.view_center[0]) * self.scale
        screen_y = height / 2 - (y - self.view_center[1]) * self.scale

        return screen_x, screen_y

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        width = self.winfo_width()
        height = self.winfo_height()

        x = self.view_center[0] + (sx - width / 2) / self.scale
        y = self.view_center[1] - (sy - height / 2) / self.scale

        return x, y

    def fit_to_points(
        self,
        points: PointsArray,
        padding: float = CAMERA_PADDING,
    ) -> None:
        """Move camera and adjust zoom so points fit into the canvas."""
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

        self.view_center = np.array(
            [
                (min_x + max_x) / 2,
                (min_y + max_y) / 2,
            ],
            dtype=float,
        )

        world_width = max(max_x - min_x, 1.0) + 2 * padding
        world_height = max(max_y - min_y, 1.0) + 2 * padding

        scale_x = width / world_width
        scale_y = height / world_height

        self.scale = max(MIN_CANVAS_SCALE, min(scale_x, scale_y))

    def draw_grid(self) -> None:
        """Draw coordinate grid and axes."""
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        self.delete("grid")

        step = calculate_grid_step(self.scale)

        left_world, top_world = self.screen_to_world(0, 0)
        right_world, bottom_world = self.screen_to_world(width, height)

        x_min = math.floor(left_world / step) * step
        x_max = math.ceil(right_world / step) * step

        y_min = math.floor(bottom_world / step) * step
        y_max = math.ceil(top_world / step) * step

        axis_x_screen, axis_y_screen = self.world_to_screen((0, 0))

        self._draw_vertical_grid_lines(x_min, x_max, step, height, axis_y_screen)
        self._draw_horizontal_grid_lines(y_min, y_max, step, width, axis_x_screen)
        self._draw_axis_labels(width, height, axis_x_screen, axis_y_screen)

    def _draw_vertical_grid_lines(
        self,
        x_min: float,
        x_max: float,
        step: float,
        height: int,
        axis_y_screen: float,
    ) -> None:
        """Draw vertical grid lines."""
        x = x_min

        while x <= x_max + step / 2:
            sx, _ = self.world_to_screen((x, 0))

            is_axis = self.is_axis(x)
            color = COLOR_AXIS if is_axis else COLOR_GRID
            line_width = self.AXIS_LINE_WIDTH if is_axis else self.GRID_LINE_WIDTH

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
                label_y = (
                    axis_y_screen + 14
                    if 0 <= axis_y_screen <= height
                    else height - 15
                )

                self.create_text(
                    sx + 10,
                    label_y,
                    text=format_number(x),
                    fill=COLOR_GRID_LABEL,
                    font=self.GRID_FONT,
                    tags="grid",
                )

            x += step

    def _draw_horizontal_grid_lines(
        self,
        y_min: float,
        y_max: float,
        step: float,
        width: int,
        axis_x_screen: float,
    ) -> None:
        """Draw horizontal grid lines."""
        y = y_min

        while y <= y_max + step / 2:
            _, sy = self.world_to_screen((0, y))

            is_axis = self.is_axis(y)
            color = COLOR_AXIS if is_axis else COLOR_GRID
            line_width = self.AXIS_LINE_WIDTH if is_axis else self.GRID_LINE_WIDTH

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
                label_x = (
                    axis_x_screen + 18
                    if 0 <= axis_x_screen <= width
                    else 20
                )

                self.create_text(
                    label_x,
                    sy - 10,
                    text=format_number(y),
                    fill=COLOR_GRID_LABEL,
                    font=self.GRID_FONT,
                    tags="grid",
                )

            y += step

    def _draw_axis_labels(
        self,
        width: int,
        height: int,
        axis_x_screen: float,
        axis_y_screen: float,
    ) -> None:
        """Draw x and y axis labels."""
        if 0 <= axis_y_screen <= height:
            self.create_text(
                width - 20,
                axis_y_screen - 15,
                text="x",
                fill=COLOR_AXIS,
                font=self.AXIS_FONT,
                tags="grid",
            )

        if 0 <= axis_x_screen <= width:
            self.create_text(
                axis_x_screen + 15,
                20,
                text="y",
                fill=COLOR_AXIS,
                font=self.AXIS_FONT,
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
        """Draw polygon edges, vertices and coordinate labels."""
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
                    width=self.POLYGON_LINE_WIDTH,
                    dash=dash,
                    tags="figure",
                )

        for index, point in enumerate(points):
            x, y = self.world_to_screen(point)

            self.create_oval(
                x - self.VERTEX_RADIUS,
                y - self.VERTEX_RADIUS,
                x + self.VERTEX_RADIUS,
                y + self.VERTEX_RADIUS,
                fill=vertex_color,
                outline="black",
                tags="figure",
            )

            text = (
                f"{label_prefix}{index + 1} "
                f"({format_number(float(point[0]))}; "
                f"{format_number(float(point[1]))})"
            )

            self.create_text(
                x + 45,
                y - 15,
                text=text,
                fill=outline,
                font=self.VERTEX_FONT,
                tags="figure",
            )

    def _find_nearest_current_vertex(self, sx: float, sy: float) -> int | None:
        """Find nearest current polygon vertex to screen point."""
        nearest_index = None
        nearest_distance = MOUSE_VERTEX_SELECTION_RADIUS

        for index, point in enumerate(self.app.current_points):
            vertex_x, vertex_y = self.world_to_screen(point)
            distance = math.hypot(sx - vertex_x, sy - vertex_y)

            if distance <= nearest_distance:
                nearest_distance = distance
                nearest_index = index

        return nearest_index

    def _on_mouse_press(self, event: tk.Event) -> None:
        """Handle mouse press on the canvas."""
        vertex_index = self._find_nearest_current_vertex(event.x, event.y)

        if vertex_index is None:
            return

        self.selected_vertex_index = vertex_index
        self.app.begin_vertex_drag()
        self.configure(cursor="hand2")

    def _on_mouse_drag(self, event: tk.Event) -> None:
        """Handle mouse dragging."""
        if self.selected_vertex_index is None:
            return

        world_position = self.screen_to_world(event.x, event.y)

        self.app.move_current_vertex(
            self.selected_vertex_index,
            world_position,
        )

        self.redraw()

    def _on_mouse_release(self, _event: tk.Event) -> None:
        """Handle mouse release."""
        if self.selected_vertex_index is None:
            return

        vertex_index = self.selected_vertex_index
        self.selected_vertex_index = None
        self.configure(cursor="")

        self.app.finish_vertex_drag(vertex_index)

    def redraw(self) -> None:
        """Clear the canvas and redraw the whole scene."""
        self.delete("all")

        self.draw_grid()

        background = self.app.background_points

        if background is not None:
            self.draw_polygon(
                background,
                outline=COLOR_BACKGROUND_OUTLINE,
                vertex_color=COLOR_BACKGROUND_VERTEX,
                dash=(5, 4),
                label_prefix=self.app.background_label_prefix,
            )

        self.draw_polygon(
            self.app.current_points,
            outline=COLOR_CURRENT_OUTLINE,
            vertex_color=COLOR_CURRENT_VERTEX,
            label_prefix="A'",
        )