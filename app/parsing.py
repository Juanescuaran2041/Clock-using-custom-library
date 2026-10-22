def parse_time(text: str) -> tuple[int, int, int]:
    """Parse 'HH:MM' or 'HH:MM:SS'. Raises ValueError if it is not a valid time."""
    parts = [int(part) for part in text.strip().split(":")]
    if len(parts) == 2:
        parts.append(0)
    if len(parts) != 3:
        raise ValueError("Expected HH:MM or HH:MM:SS")
    hours, minutes, seconds = parts
    if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
        raise ValueError("Time out of range")
    return hours, minutes, seconds
