from core.clock_reading import ClockReading
from graphics.canvas import LEFT, Canvas, Point
from graphics.hands import HourHand, MinuteHand, SecondHand
from graphics.math_utils import cos, degrees_to_radians, sin
from graphics.palette import BACKGROUND, GRAY, NAVY, ORANGE, PURPLE, RED
from graphics.shapes import Circle, FilledCircle, Line, Rectangle, Text

MINUTES_ON_DIAL = 60
HOURS_ON_DIAL = 12
DEGREES_PER_MINUTE = 6
DEGREES_PER_HOUR = 30
COMMAND_BAR_HEIGHT = 56


class AnalogFace:
    def __init__(self, center: Point, radius: int) -> None:
        self.__center = center
        self.__radius = radius
        self.__hands = (HourHand(), MinuteHand(), SecondHand())

    def draw(self, canvas: Canvas, reading: ClockReading) -> None:
        Circle(self.__center, self.__radius, NAVY, 4).draw(canvas)
        self.__draw_ticks(canvas)
        self.__draw_numbers(canvas)
        for hand in self.__hands:
            hand.draw(canvas, self.__center, self.__radius, reading)
        FilledCircle(self.__center, 7, NAVY).draw(canvas)

    def __point_on_dial(self, degrees: float, radius_ratio: float) -> Point:
        radians = degrees_to_radians(degrees)
        distance = self.__radius * radius_ratio
        return Point(round(self.__center.x + distance * sin(radians)),
                     round(self.__center.y - distance * cos(radians)))

    def __draw_ticks(self, canvas: Canvas) -> None:
        for minute in range(MINUTES_ON_DIAL):
            is_hour_mark = minute % 5 == 0
            inner_ratio = 0.86 if is_hour_mark else 0.92
            degrees = minute * DEGREES_PER_MINUTE
            Line(self.__point_on_dial(degrees, inner_ratio),
                 self.__point_on_dial(degrees, 0.96),
                 NAVY, 3 if is_hour_mark else 1).draw(canvas)

    def __draw_numbers(self, canvas: Canvas) -> None:
        for hour in range(1, HOURS_ON_DIAL + 1):
            position = self.__point_on_dial(hour * DEGREES_PER_HOUR, 0.72)
            Text.centered_at(position, str(hour), NAVY, 20, bold=True).draw(canvas)


class DigitalDisplay:
    def __init__(self, left: int) -> None:
        self.__left = left

    def draw(self, canvas: Canvas, reading: ClockReading) -> None:
        left = self.__left
        Text(Point(left, 70), reading.zone_name, PURPLE, 28, LEFT, bold=True).draw(canvas)
        Text(Point(left, 140), reading.time_text(), NAVY, 64, LEFT, bold=True,
             mono=True).draw(canvas)
        Text(Point(left, 215), reading.alarm_label, NAVY, 24, LEFT).draw(canvas)
        if reading.alarm_ringing:
            Text(Point(left, 262), "RINGING", RED, 38, LEFT, bold=True).draw(canvas)


class CommandBar:
    """The strip at the bottom where commands are typed and answers are shown."""

    def __init__(self, width: int, height: int) -> None:
        self.__top = height - COMMAND_BAR_HEIGHT
        self.__width = width

    def draw(self, canvas: Canvas, typed: str, message: str, show_cursor: bool) -> None:
        Rectangle(0, self.__top, self.__width, 1, GRAY, 1, True).draw(canvas)
        cursor = "_" if show_cursor else " "
        Text(Point(16, self.__top + 16), f"> {typed}{cursor}", NAVY, 18, LEFT,
             mono=True).draw(canvas)
        Text(Point(16, self.__top + 40), message, GRAY, 14, LEFT).draw(canvas)


class ClockView:
    """Composes the analog face, the digital display, the command bar and the alarm frame."""

    def __init__(self, width: int, height: int) -> None:
        self.__width = width
        self.__height = height
        self.__face = AnalogFace(Point(170, (height - COMMAND_BAR_HEIGHT) // 2), 140)
        self.__digital = DigitalDisplay(350)
        self.__command_bar = CommandBar(width, height)

    def render(self, canvas: Canvas, reading: ClockReading, typed: str, message: str,
               show_cursor: bool) -> None:
        canvas.fill(BACKGROUND)
        self.__face.draw(canvas, reading)
        self.__digital.draw(canvas, reading)
        self.__command_bar.draw(canvas, typed, message, show_cursor)
        if reading.alarm_ringing:
            Rectangle(0, 0, self.__width, self.__height, RED, 6).draw(canvas)
        else:
            Rectangle(0, 0, self.__width, self.__height, ORANGE, 2).draw(canvas)
        canvas.present()
