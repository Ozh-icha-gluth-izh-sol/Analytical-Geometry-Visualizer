import math
import tkinter as tk

import customtkinter as ctk
import numpy as np

from geometry_visualizer.canvas import GeometryCanvas
from geometry_visualizer.config import MAX_INPUT_ABS_VALUE, MIN_SCALE_FACTOR, AppConfig
from geometry_visualizer.errors import InvalidInputError, InvalidScaleError
from geometry_visualizer.transformations import (
    figure_center,
    rotate_points,
    scale_points,
    translate_points,
)
from geometry_visualizer.types import PointArray, PointsArray


class GeometryTransformApp(ctk.CTk):
    """
    The class creates the user interface, stores polygon state and applies
    geometric transformations requested by the user.
    """

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialize application window and default polygon.

        Args:
            config: Optional application configuration.
        """
        super().__init__()

        self.config = config or AppConfig.default()

        self.title(self.config.title)
        self.geometry(self.config.window_size)
        self.minsize(*self.config.min_window_size)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.original_points = self.config.initial_points.copy()
        self.current_points = self.config.initial_points.copy()

        self.create_layout()
        self.after(100, self.update_canvas_view)

    @property
    def transform_center(self) -> PointArray:
        """
        Returns:
            Origin point or current figure center depending on selected mode.
        """
        if self.center_mode.get() == "origin":
            return np.array([0.0, 0.0], dtype=float)

        return figure_center(self.current_points)

    @property
    def visible_points(self) -> PointsArray:
        """
        Returns:
            Current polygon points. The original polygon is still drawn, but the
            camera follows the transformed figure.
        """
        return self.current_points

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

        self.control_panel = ctk.CTkFrame(self, width=300)
        self.control_panel.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        self.control_panel.grid_propagate(False)

        title = ctk.CTkLabel(
            self.control_panel,
            text="Преобразования",
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=(20, 15))

        self.create_translate_controls()
        self.create_rotate_controls()
        self.create_scale_controls()
        self.create_common_controls()

    def create_translate_controls(self) -> None:
        """Create controls for translation."""
        frame = ctk.CTkFrame(self.control_panel)
        frame.pack(fill="x", padx=15, pady=10)

        label = ctk.CTkLabel(
            frame,
            text="Перенос",
            font=("Arial", 16, "bold"),
        )
        label.pack(pady=(10, 5))

        self.dx_entry = ctk.CTkEntry(frame, placeholder_text="dx")
        self.dx_entry.insert(0, "1")
        self.dx_entry.pack(fill="x", padx=10, pady=5)

        self.dy_entry = ctk.CTkEntry(frame, placeholder_text="dy")
        self.dy_entry.insert(0, "1")
        self.dy_entry.pack(fill="x", padx=10, pady=5)

        button = ctk.CTkButton(
            frame,
            text="Применить перенос",
            command=self.apply_translation,
        )
        button.pack(fill="x", padx=10, pady=(5, 10))

    def create_rotate_controls(self) -> None:
        """Create controls for rotation."""
        frame = ctk.CTkFrame(self.control_panel)
        frame.pack(fill="x", padx=15, pady=10)

        label = ctk.CTkLabel(
            frame,
            text="Поворот",
            font=("Arial", 16, "bold"),
        )
        label.pack(pady=(10, 5))

        self.angle_entry = ctk.CTkEntry(frame, placeholder_text="угол в градусах")
        self.angle_entry.insert(0, "45")
        self.angle_entry.pack(fill="x", padx=10, pady=5)

        button = ctk.CTkButton(
            frame,
            text="Повернуть",
            command=self.apply_rotation,
        )
        button.pack(fill="x", padx=10, pady=(5, 10))

    def create_scale_controls(self) -> None:
        """Create controls for scaling."""
        frame = ctk.CTkFrame(self.control_panel)
        frame.pack(fill="x", padx=15, pady=10)

        label = ctk.CTkLabel(
            frame,
            text="Масштабирование",
            font=("Arial", 16, "bold"),
        )
        label.pack(pady=(10, 5))

        self.sx_entry = ctk.CTkEntry(frame, placeholder_text="kx")
        self.sx_entry.insert(0, "1.5")
        self.sx_entry.pack(fill="x", padx=10, pady=5)

        self.sy_entry = ctk.CTkEntry(frame, placeholder_text="ky")
        self.sy_entry.insert(0, "1.5")
        self.sy_entry.pack(fill="x", padx=10, pady=5)

        button = ctk.CTkButton(
            frame,
            text="Применить масштаб",
            command=self.apply_scaling,
        )
        button.pack(fill="x", padx=10, pady=(5, 10))

    def create_common_controls(self) -> None:
        """Create common controls shared by all transformations."""
        frame = ctk.CTkFrame(self.control_panel)
        frame.pack(fill="x", padx=15, pady=10)

        self.center_mode = tk.StringVar(value="origin")

        label = ctk.CTkLabel(
            frame,
            text="Центр преобразования",
            font=("Arial", 16, "bold"),
        )
        label.pack(pady=(10, 5))

        origin_radio = ctk.CTkRadioButton(
            frame,
            text="Начало координат",
            variable=self.center_mode,
            value="origin",
        )
        origin_radio.pack(anchor="w", padx=10, pady=3)

        figure_radio = ctk.CTkRadioButton(
            frame,
            text="Центр фигуры",
            variable=self.center_mode,
            value="figure",
        )
        figure_radio.pack(anchor="w", padx=10, pady=3)

        reset_button = ctk.CTkButton(
            frame,
            text="Сбросить фигуру",
            fg_color="#666666",
            hover_color="#444444",
            command=self.reset_figure,
        )
        reset_button.pack(fill="x", padx=10, pady=(15, 10))

        self.status_label = ctk.CTkLabel(
            self.control_panel,
            text="Серая фигура — исходная, синяя — текущая.",
            wraplength=250,
            text_color="#444444",
        )
        self.status_label.pack(padx=15, pady=10)

    def update_canvas_view(self) -> None:
        """Update camera, zoom level and redraw the canvas."""
        self.canvas.fit_to_points(self.visible_points)
        self.canvas.redraw()

    def read_float(self, entry: ctk.CTkEntry, name: str) -> float | None:
        """Read and validate a float value from an entry.

        Args:
            entry: Entry widget.
            name: Human-readable field name.

        Returns:
            Parsed float value or None if validation failed.
        """
        try:
            return self.parse_float(entry.get(), name)
        except InvalidInputError as exc:
            self.status_label.configure(text=f"Ошибка: {exc}")
            return None

    def parse_float(self, value: str, name: str) -> float:
        """Parse a finite float value from a string.

        Args:
            value: Raw text from input field.
            name: Human-readable field name.

        Raises:
            InvalidInputError

        Returns:
            Parsed float value.
        """
        value = value.strip().replace(",", ".")

        if not value:
            raise InvalidInputError(f"поле {name} не должно быть пустым.")

        try:
            result = float(value)
        except ValueError as exc:
            raise InvalidInputError(f"поле {name} должно быть числом.") from exc

        if not math.isfinite(result):
            raise InvalidInputError(f"поле {name} должно быть конечным числом.")

        if abs(result) > MAX_INPUT_ABS_VALUE:
            raise InvalidInputError(
                f"поле {name} слишком большое. " f"Максимум: {MAX_INPUT_ABS_VALUE}."
            )

        return result

    def validate_scale(self, sx: float, sy: float) -> None:
        """Validate scale coefficients.

        Args:
            sx: Scale coefficient along the x-axis.
            sy: Scale coefficient along the y-axis.

        Raises:
            InvalidScaleError
        """
        if abs(sx) < MIN_SCALE_FACTOR or abs(sy) < MIN_SCALE_FACTOR:
            raise InvalidScaleError("коэффициенты масштаба не должны быть равны 0.")

    def apply_translation(self) -> None:
        """Apply translation to the current figure."""
        dx = self.read_float(self.dx_entry, "dx")
        dy = self.read_float(self.dy_entry, "dy")

        if dx is None or dy is None:
            return

        self.current_points = translate_points(self.current_points, dx, dy)

        self.status_label.configure(text=f"Выполнен перенос на вектор ({dx}; {dy}).")
        self.update_canvas_view()

    def apply_rotation(self) -> None:
        """Apply rotation to the current figure."""
        angle = self.read_float(self.angle_entry, "угол")

        if angle is None:
            return

        self.current_points = rotate_points(
            self.current_points,
            angle,
            self.transform_center,
        )

        self.status_label.configure(text=f"Выполнен поворот на {angle}°.")
        self.update_canvas_view()

    def apply_scaling(self) -> None:
        """Apply scaling to the current figure."""
        sx = self.read_float(self.sx_entry, "kx")
        sy = self.read_float(self.sy_entry, "ky")

        if sx is None or sy is None:
            return

        try:
            self.validate_scale(sx, sy)
        except InvalidScaleError as exc:
            self.status_label.configure(text=f"Ошибка: {exc}")
            return

        self.current_points = scale_points(
            self.current_points,
            sx,
            sy,
            self.transform_center,
        )

        self.status_label.configure(text=f"Выполнено масштабирование kx={sx}, ky={sy}.")
        self.update_canvas_view()

    def reset_figure(self) -> None:
        """Reset current figure to its initial state."""
        self.current_points = self.original_points.copy()

        self.status_label.configure(text="Фигура сброшена в исходное состояние.")
        self.update_canvas_view()
