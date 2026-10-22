import clocklib

PI = 3.141592653589793


def degrees_to_radians(degrees: float) -> float:
    return degrees * PI / 180


def sin(angle: float) -> float:
    return clocklib.sin(angle)


def cos(angle: float) -> float:
    return clocklib.cos(angle)
