class GeometryVisualizerError(Exception):
    """Base exception for geometry visualizer erros."""
    pass


class InvalidInputError(ValueError):
    """Raised when user input cannot be converted to a valid number."""
    pass


class InvalidScaleError(InvalidInputError):
    """Raised when scale coefficient is invalid."""
    pass
