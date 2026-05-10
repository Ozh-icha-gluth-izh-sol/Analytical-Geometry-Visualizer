import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk

from geometry_visualizer.config import (
    PANEL_WIDTH,
    TEXT_HISTORY_INITIAL,
)
from geometry_visualizer.enum import BackgroundFigureMode, TransformCenterMode


class TransformControlPanel(ctk.CTkScrollableFrame):
    """Panel with all transformation and display controls."""

    def __init__(
        self,
        master: tk.Misc,
        on_translate: Callable[[], None],
        on_rotate: Callable[[], None],
        on_scale: Callable[[], None],
        on_reflect_x: Callable[[], None],
        on_reflect_y: Callable[[], None],
        on_reset: Callable[[], None],
        on_display_mode_change: Callable[[], None],
        on_control_snapshot_change: Callable[[str], None],
    ) -> None:
        """Initialize the control panel."""
        super().__init__(master, width=PANEL_WIDTH)

        self.center_mode = tk.StringVar(value=TransformCenterMode.ORIGIN.value)
        self.background_mode = tk.StringVar(
            value=BackgroundFigureMode.CURRENT_ONLY.value,
        )
        self.history_snapshot = tk.StringVar(value=TEXT_HISTORY_INITIAL)

        self._on_translate = on_translate
        self._on_rotate = on_rotate
        self._on_scale = on_scale
        self._on_reflect_x = on_reflect_x
        self._on_reflect_y = on_reflect_y
        self._on_reset = on_reset
        self._on_display_mode_change = on_display_mode_change
        self._on_control_snapshot_change = on_control_snapshot_change

        self._create_widgets()

    @property
    def dx_text(self) -> str:
        """Return raw dx input."""
        return self.dx_entry.get()

    @property
    def dy_text(self) -> str:
        """Return raw dy input."""
        return self.dy_entry.get()

    @property
    def angle_text(self) -> str:
        """Return raw angle input."""
        return self.angle_entry.get()

    @property
    def sx_text(self) -> str:
        """Return raw x-scale input."""
        return self.sx_entry.get()

    @property
    def sy_text(self) -> str:
        """Return raw y-scale input."""
        return self.sy_entry.get()

    @property
    def center_mode_value(self) -> TransformCenterMode:
        """Return selected transformation center mode."""
        return TransformCenterMode(self.center_mode.get())

    @property
    def background_mode_value(self) -> BackgroundFigureMode:
        """Return selected background figure mode."""
        return BackgroundFigureMode(self.background_mode.get())

    def set_status(self, text: str) -> None:
        """Set status label text."""
        self.status_label.configure(text=text)

    def set_history_options(self, labels: list[str]) -> None:
        """Update available history snapshots."""
        if not labels:
            return

        self.history_menu.configure(values=labels)

        if self.history_snapshot.get() not in labels:
            self.history_snapshot.set(labels[0])

        self._update_action_history(labels)

    def _create_widgets(self) -> None:
        """Create all panel widgets."""
        title = ctk.CTkLabel(
            self,
            text="Преобразования",
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=(20, 15))

        self._create_translate_controls()
        self._create_rotate_controls()
        self._create_scale_controls()
        self._create_reflection_controls()
        self._create_display_controls()
        self._create_center_controls()
        self._create_reset_and_status()

    def _create_section_frame(self, title: str) -> ctk.CTkFrame:
        """Create a section frame with title."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=15, pady=10)

        label = ctk.CTkLabel(frame, text=title, font=("Arial", 16, "bold"))
        label.pack(pady=(10, 5))

        return frame

    def _create_entry(
        self,
        frame: ctk.CTkFrame,
        placeholder: str,
        default_value: str,
    ) -> ctk.CTkEntry:
        """Create entry with default value."""
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder)
        entry.insert(0, default_value)
        entry.pack(fill="x", padx=10, pady=5)
        return entry

    def _create_button(
        self,
        frame: ctk.CTkFrame,
        text: str,
        command: Callable[[], None],
    ) -> None:
        """Create full-width button."""
        button = ctk.CTkButton(frame, text=text, command=command)
        button.pack(fill="x", padx=10, pady=(5, 10))

    def _create_translate_controls(self) -> None:
        """Create translation controls."""
        frame = self._create_section_frame("Перенос")

        self.dx_entry = self._create_entry(frame, "dx", "1")
        self.dy_entry = self._create_entry(frame, "dy", "1")

        self._create_button(frame, "Применить перенос", self._on_translate)

    def _create_rotate_controls(self) -> None:
        """Create rotation controls."""
        frame = self._create_section_frame("Поворот")

        self.angle_entry = self._create_entry(frame, "угол в градусах", "45")

        self._create_button(frame, "Повернуть", self._on_rotate)

    def _create_scale_controls(self) -> None:
        """Create scaling controls."""
        frame = self._create_section_frame("Масштабирование")

        self.sx_entry = self._create_entry(frame, "kx", "1.5")
        self.sy_entry = self._create_entry(frame, "ky", "1.5")

        self._create_button(frame, "Применить масштаб", self._on_scale)

    def _create_reflection_controls(self) -> None:
        """Create reflection controls."""
        frame = self._create_section_frame("Отражение")

        self._create_button(frame, "Отразить относительно Ox", self._on_reflect_x)
        self._create_button(frame, "Отразить относительно Oy", self._on_reflect_y)

    def _create_display_controls(self) -> None:
        """Create background figure display controls."""
        frame = self._create_section_frame("Сравнение фигур")

        self.background_mode_menu = ctk.CTkOptionMenu(
            frame,
            values=[mode.value for mode in BackgroundFigureMode],
            variable=self.background_mode,
            command=lambda _: self._on_display_mode_change(),
        )
        self.background_mode_menu.pack(fill="x", padx=10, pady=5)

        history_label = ctk.CTkLabel(
            frame,
            text="Контрольная фигура из истории",
            font=("Arial", 14, "bold"),
        )
        history_label.pack(pady=(10, 5))

        self.history_menu = ctk.CTkOptionMenu(
            frame,
            values=[TEXT_HISTORY_INITIAL],
            variable=self.history_snapshot,
            command=self._on_control_snapshot_change,
        )
        self.history_menu.pack(fill="x", padx=10, pady=(5, 10))

        action_history_label = ctk.CTkLabel(
            frame,
            text="История действий",
            font=("Arial", 14, "bold"),
        )
        action_history_label.pack(pady=(10, 5))

        self.action_history = ctk.CTkTextbox(frame, height=90)
        self.action_history.pack(fill="x", padx=10, pady=(5, 10))
        self.action_history.configure(state="disabled")

    def _create_center_controls(self) -> None:
        """Create transformation center controls."""
        frame = self._create_section_frame("Центр преобразования")

        origin_radio = ctk.CTkRadioButton(
            frame,
            text="Начало координат",
            variable=self.center_mode,
            value=TransformCenterMode.ORIGIN.value,
        )
        origin_radio.pack(anchor="w", padx=10, pady=3)

        figure_radio = ctk.CTkRadioButton(
            frame,
            text="Центр фигуры",
            variable=self.center_mode,
            value=TransformCenterMode.FIGURE.value,
        )
        figure_radio.pack(anchor="w", padx=10, pady=3)

    def _create_reset_and_status(self) -> None:
        """Create reset button and status label."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=15, pady=10)

        reset_button = ctk.CTkButton(
            frame,
            text="Сбросить фигуру",
            fg_color="#666666",
            hover_color="#444444",
            command=self._on_reset,
        )
        reset_button.pack(fill="x", padx=10, pady=(15, 10))

        self.status_label = ctk.CTkLabel(
            self,
            text="Готово.",
            wraplength=250,
            text_color="#444444",
        )
        self.status_label.pack(padx=15, pady=10)

    def _update_action_history(self, labels: list[str]) -> None:
        """Update visible action history list."""
        self.action_history.configure(state="normal")
        self.action_history.delete("1.0", "end")
        self.action_history.insert("end", "\n".join(labels))
        self.action_history.configure(state="disabled")