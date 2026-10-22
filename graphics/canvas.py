import clocklib

Color = tuple[int, int, int]  # (red, green, blue), each from 0 to 255

LEFT = 0
CENTER = 1
RIGHT = 2


class Point:
    """An immutable position on the canvas."""

    def __init__(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y


class Canvas:
    """The drawing surface of a native window. The origin (0, 0) is the top-left corner."""

    def __init__(self, title: str, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Canvas dimensions must be positive")
        self.__width = width
        self.__height = height
        self.__window = clocklib.Window(title, width, height)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def is_open(self) -> bool:
        return self.__window.is_open()

    def fill(self, color: Color) -> None:
        self.__window.fill(color)

    def draw_line(self, start: Point, end: Point, color: Color, thickness: int) -> None:
        self.__window.line(start.x, start.y, end.x, end.y, color, thickness)

    def draw_circle(self, center: Point, radius: int, color: Color, thickness: int) -> None:
        self.__window.circle(center.x, center.y, radius, color, thickness)

    def draw_filled_circle(self, center: Point, radius: int, color: Color) -> None:
        self.__window.fill_circle(center.x, center.y, radius, color)

    def draw_rectangle(self, x: int, y: int, width: int, height: int, color: Color,
                       thickness: int, filled: bool = False) -> None:
        self.__window.rect(x, y, width, height, color, thickness, filled)

    def draw_text(self, position: Point, text: str, color: Color, size: int,
                  align: int = LEFT, bold: bool = False, mono: bool = False) -> None:
        self.__window.text(position.x, position.y, text, color, size, align, bold, mono)

    def present(self) -> None:
        self.__window.present()

    def events(self) -> list[int]:
        """Character codes typed since the last call. Also keeps the window responsive."""
        return self.__window.poll()

    def save_bmp(self, path: str) -> None:
        self.__window.save_bmp(path)

    def close(self) -> None:
        self.__window.close()
