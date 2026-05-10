import math

import customtkinter as ctk
import numpy as np

from geometry_visualizer.canvas import GeometryCanvas
from geometry_visualizer.config import (
    MAX_INPUT_ABS_VALUE,
    MIN_SCALE_FACTOR,
    TEXT_HISTORY_INITIAL,
    TEXT_NO_PREVIOUS_FIGURE,
    TEXT_VERTEX_DRAGGED,
    AppConfig,
)
from geometry_visualizer.control_panel import TransformControlPanel
from geometry_visualizer.enum import BackgroundFigureMode, TransformCenterMode
from geometry_visualizer.errors import InvalidInputError, InvalidScaleError
from geometry_visualizer.transformations import (
    figure_center,
    reflect_x_axis,
    reflect_y_axis,
    rotate_points,
    scale_points,
    translate_points,
)
from geometry_visualizer.types import PointArray, PointsArray


class GeometryTransformApp(ctk.CTk):
    """Main application class."""

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialize application window and polygon state."""
        super().__init__()

        self.config = config or AppConfig.default()

        self.title(self.config.title)
        self.geometry(self.config.window_size)
        self.minsize(*self.config.min_window_size)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.original_points = self.config.initial_points.copy()
        self.current_points = self.config.initial_points.copy()
        self.previous_points: PointsArray | None = None

        self.history_points: list[PointsArray] = [self.current_points.copy()]
        self.history_labels: list[str] = [TEXT_HISTORY_INITIAL]
        self.control_snapshot_index = 0

        self._drag_start_points: PointsArray | None = None

        self.create_layout()
        self.control_panel.set_history_options(self.history_labels)

        self.after(100, self.update_canvas_view)

    @property
    def transform_center(self) -> PointArray:
        """Return the current center of transformation."""
        if self.control_panel.center_mode_value == TransformCenterMode.ORIGIN:
            return np.array([0.0, 0.0], dtype=float)

        return figure_center(self.current_points)

    @property
    def background_points(self) -> PointsArray | None:
        """Return points of the selected background figure."""
        if not hasattr(self, "control_panel"):
            return None

        mode = self.control_panel.background_mode_value

        if mode == BackgroundFigureMode.ORIGINAL:
            return self.original_points

        if mode == BackgroundFigureMode.PREVIOUS:
            return self.previous_points

        if mode == BackgroundFigureMode.CONTROL:
            return self.history_points[self.control_snapshot_index]

        return None

    @property
    def background_label_prefix(self) -> str:
        """Return label prefix for the selected background figure."""
        if not hasattr(self, "control_panel"):
            return ""

        mode = self.control_panel.background_mode_value

        if mode == BackgroundFigureMode.ORIGINAL:
            return "A"

        if mode == BackgroundFigureMode.PREVIOUS:
            return "P"

        if mode == BackgroundFigureMode.CONTROL:
            return "C"

        return ""

    @property
    def visible_points(self) -> PointsArray:
        """Return points used for automatic camera fitting."""
        background = self.background_points

        if background is None:
            return self.current_points

        return np.vstack([background, self.current_points])

    def create_layout(self) -> None:
        """Create the main window layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.canvas = GeometryCanvas(
            self,
            app=self,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.control_panel = TransformControlPanel(
            self,
            on_translate=self.apply_translation,
            on_rotate=self.apply_rotation,
            on_scale=self.apply_scaling,
            on_reflect_x=self.apply_reflection_x,
            on_reflect_y=self.apply_reflection_y,
            on_reset=self.reset_figure,
            on_display_mode_change=self.update_canvas_view,
            on_control_snapshot_change=self.select_control_snapshot,
        )
        self.control_panel.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

    def update_canvas_view(self) -> None:
        """Update camera, zoom level and redraw the canvas."""
        if (
            self.control_panel.background_mode_value == BackgroundFigureMode.PREVIOUS
            and self.previous_points is None
        ):
            self.show_status(TEXT_NO_PREVIOUS_FIGURE)

        self.canvas.fit_to_points(self.visible_points)
        self.canvas.redraw()

    def show_error(self, message: str) -> None:
        """Display an error message."""
        self.control_panel.set_status(f"Ошибка: {message}")

    def show_status(self, message: str) -> None:
        """Display a regular status message."""
        self.control_panel.set_status(message)

    def read_float(self, value: str, name: str) -> float | None:
        """Read and validate a float value from raw text."""
        try:
            return self.parse_float(value, name)
        except InvalidInputError as exc:
            self.show_error(str(exc))
            return None

    def parse_float(self, value: str, name: str) -> float:
        """Parse a finite float value from a string."""
        value = value.strip().replace(",", ".")

        if not value:
            raise InvalidInputError(f"{name} не должно быть пустым.")

        try:
            result = float(value)
        except ValueError as exc:
            raise InvalidInputError(f"{name} должно быть числом.") from exc

        if not math.isfinite(result):
            raise InvalidInputError(f"{name} должно быть конечным числом.")

        if abs(result) > MAX_INPUT_ABS_VALUE:
            raise InvalidInputError(
                f"{name} слишком большое. Максимум: {MAX_INPUT_ABS_VALUE}."
            )

        return result

    def validate_scale(self, sx: float, sy: float) -> None:
        """Validate scale coefficients."""
        if abs(sx) < MIN_SCALE_FACTOR or abs(sy) < MIN_SCALE_FACTOR:
            raise InvalidScaleError("коэффициенты масштаба не должны быть равны 0.")

    def apply_transformation(
        self,
        history_label: str,
        new_points: PointsArray,
        status: str | None = None,
    ) -> None:
        """Apply new points, save history and update canvas."""
        self.save_previous_state()
        self.current_points = new_points
        self.add_history_snapshot(history_label)

        self.show_status(status or f"Выполнено: {history_label}.")
        self.update_canvas_view()

    def save_previous_state(self) -> None:
        """Save current figure before applying a new transformation."""
        self.previous_points = self.current_points.copy()

    def add_history_snapshot(self, label: str) -> None:
        """Save current figure state to history."""
        index = len(self.history_points)

        self.history_points.append(self.current_points.copy())
        self.history_labels.append(f"{index}: {label}")

        self.control_panel.set_history_options(self.history_labels)

    def select_control_snapshot(self, selected_label: str) -> None:
        """Select a history snapshot as a control figure."""
        if selected_label not in self.history_labels:
            return

        self.control_snapshot_index = self.history_labels.index(selected_label)
        self.update_canvas_view()

    def begin_vertex_drag(self) -> None:
        """Save state before vertex dragging starts."""
        if self._drag_start_points is not None:
            return

        self._drag_start_points = self.current_points.copy()
        self.previous_points = self.current_points.copy()

    def move_current_vertex(
        self,
        vertex_index: int,
        new_position: tuple[float, float],
    ) -> None:
        """Move one vertex of the current polygon."""
        self.current_points[vertex_index] = np.array(new_position, dtype=float)

    def finish_vertex_drag(self, vertex_index: int) -> None:
        """Finish vertex dragging and add action to history."""
        if self._drag_start_points is None:
            return

        was_changed = not np.allclose(self._drag_start_points, self.current_points)

        if was_changed:
            self.add_history_snapshot(f"Перетаскивание вершины {vertex_index + 1}")
            self.show_status(TEXT_VERTEX_DRAGGED)

        self._drag_start_points = None
        self.update_canvas_view()

    def apply_translation(self) -> None:
        """Apply translation to the current figure."""
        dx = self.read_float(self.control_panel.dx_text, "dx")
        dy = self.read_float(self.control_panel.dy_text, "dy")

        if dx is None or dy is None:
            return

        self.apply_transformation(
            f"Перенос ({dx}; {dy})",
            translate_points(self.current_points, dx, dy),
        )

    def apply_rotation(self) -> None:
        """Apply rotation to the current figure."""
        angle = self.read_float(self.control_panel.angle_text, "угол")

        if angle is None:
            return

        self.apply_transformation(
            f"Поворот {angle}°",
            rotate_points(self.current_points, angle, self.transform_center),
        )

    def apply_scaling(self) -> None:
        """Apply scaling to the current figure."""
        sx = self.read_float(self.control_panel.sx_text, "kx")
        sy = self.read_float(self.control_panel.sy_text, "ky")

        if sx is None or sy is None:
            return

        try:
            self.validate_scale(sx, sy)
        except InvalidScaleError as exc:
            self.show_error(str(exc))
            return

        self.apply_transformation(
            f"Масштаб kx={sx}, ky={sy}",
            scale_points(self.current_points, sx, sy, self.transform_center),
        )

    def apply_reflection_x(self) -> None:
        """Reflect current figure relative to the x-axis."""
        self.apply_transformation(
            "Отражение относительно Ox",
            reflect_x_axis(self.current_points),
        )

    def apply_reflection_y(self) -> None:
        """Reflect current figure relative to the y-axis."""
        self.apply_transformation(
            "Отражение относительно Oy",
            reflect_y_axis(self.current_points),
        )

    def reset_figure(self) -> None:
        """Reset current figure to its initial state."""
        self.apply_transformation(
            "Сброс",
            self.original_points.copy(),
            status="Фигура сброшена в исходное состояние.",
        )