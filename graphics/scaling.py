def scaled(value: int, factor: float) -> int:
    """A thickness or size multiplied by a factor, never smaller than 1 pixel."""
    return max(1, round(value * factor))
