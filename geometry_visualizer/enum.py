from enum import StrEnum


class TransformCenterMode(StrEnum):
    ORIGIN = "origin"
    FIGURE = "figure"


class BackgroundFigureMode(StrEnum):
    CURRENT_ONLY = "Только текущая"
    ORIGINAL = "Исходная"
    PREVIOUS = "Предыдущая"
    CONTROL = "Контрольная"