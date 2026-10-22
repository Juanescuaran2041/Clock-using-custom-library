from core.clock_reading import ClockReading
from graphics.canvas import Canvas, Color, Point
from graphics.math_utils import cos, degrees_to_radians, sin
from graphics.palette import NAVY, RED
from graphics.scaling import scaled
from graphics.shapes import Line


class Hand:
    """Base class of the clock hands. Each subclass decides its own angle."""

    def __init__(self, length_ratio: float, color: Color, thickness: int) -> None:
        self._length_ratio = length_ratio
        self._color = color
        self._thickness = thickness

    def angle(self, reading: ClockReading) -> float:
        """Degrees measured clockwise from the 12."""
        raise NotImplementedError("Each hand computes its own angle")

    def draw(self, canvas: Canvas, center: Point, radius: int, reading: ClockReading,
             detail: float = 1.0) -> None:
        radians = degrees_to_radians(self.angle(reading))
        length = radius * self._length_ratio
        tip = Point(round(center.x + length * sin(radians)),
                    round(center.y - length * cos(radians)))
        Line(center, tip, self._color, scaled(self._thickness, detail)).draw(canvas)


class HourHand(Hand):
    def __init__(self) -> None:
        super().__init__(0.5, NAVY, 7)

    def angle(self, reading: ClockReading) -> float:
        return (reading.hours % 12) * 30 + reading.minutes * 0.5 + reading.seconds / 120


class MinuteHand(Hand):
    def __init__(self) -> None:
        super().__init__(0.75, NAVY, 4)

    def angle(self, reading: ClockReading) -> float:
        return reading.minutes * 6 + reading.seconds * 0.1


class SecondHand(Hand):
    def __init__(self) -> None:
        super().__init__(0.88, RED, 2)

    def angle(self, reading: ClockReading) -> float:
        return reading.seconds * 6
