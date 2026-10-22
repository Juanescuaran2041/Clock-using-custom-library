from graphics.canvas import CENTER, Canvas, Color, Point


class Shape:
    """Base class of everything that can be drawn. Each subclass knows how to draw itself."""

    def __init__(self, color: Color) -> None:
        self._color = color

    def draw(self, canvas: Canvas) -> None:
        raise NotImplementedError("Each shape draws itself")


class Line(Shape):
    def __init__(self, start: Point, end: Point, color: Color, thickness: int = 1) -> None:
        super().__init__(color)
        self.__start = start
        self.__end = end
        self.__thickness = thickness

    def draw(self, canvas: Canvas) -> None:
        canvas.draw_line(self.__start, self.__end, self._color, self.__thickness)


class Circle(Shape):
    def __init__(self, center: Point, radius: int, color: Color, thickness: int = 1) -> None:
        super().__init__(color)
        self._center = center
        self._radius = radius
        self._thickness = thickness

    def draw(self, canvas: Canvas) -> None:
        canvas.draw_circle(self._center, self._radius, self._color, self._thickness)


class FilledCircle(Circle):
    def __init__(self, center: Point, radius: int, color: Color) -> None:
        super().__init__(center, radius, color)

    def draw(self, canvas: Canvas) -> None:
        canvas.draw_filled_circle(self._center, self._radius, self._color)


class Rectangle(Shape):
    def __init__(self, x: int, y: int, width: int, height: int, color: Color,
                 thickness: int = 1, filled: bool = False) -> None:
        super().__init__(color)
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__thickness = thickness
        self.__filled = filled

    def draw(self, canvas: Canvas) -> None:
        canvas.draw_rectangle(self.__x, self.__y, self.__width, self.__height, self._color,
                              self.__thickness, self.__filled)


class Text(Shape):
    """Text whose vertical middle is at the given position."""

    def __init__(self, position: Point, text: str, color: Color, size: int,
                 align: int = 0, bold: bool = False, mono: bool = False) -> None:
        super().__init__(color)
        self.__position = position
        self.__text = text
        self.__size = size
        self.__align = align
        self.__bold = bold
        self.__mono = mono

    @classmethod
    def centered_at(cls, position: Point, text: str, color: Color, size: int,
                    bold: bool = False) -> "Text":
        return cls(position, text, color, size, CENTER, bold)

    def draw(self, canvas: Canvas) -> None:
        canvas.draw_text(self.__position, self.__text, self._color, self.__size,
                         self.__align, self.__bold, self.__mono)
