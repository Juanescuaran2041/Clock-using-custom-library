class Mark:
    def __init__(self, value: int) -> None:
        self.__value = value
        self.__next: "Mark" = self  # a lone mark points to itself

    @property
    def value(self) -> int:
        return self.__value

    @property
    def next(self) -> "Mark":
        return self.__next

    @next.setter
    def next(self, mark: "Mark") -> None:
        self.__next = mark

class Dial:

    def __init__(self) -> None:
        self.__first: Mark | None = None
        self.__last: Mark | None = None
        self.__size = 0
        self.__current: Mark | None = None

    @property
    def first_mark(self) -> Mark:
        if self.__first is None:
            raise ValueError("The dial is empty")
        return self.__first

    @property
    def current_value(self) -> int:
        if self.__current is None:
            raise ValueError("The dial is empty")
        return self.__current.value

    def __len__(self) -> int:
        return self.__size

    def __iter__(self):
        mark = self.__first
        for _ in range(self.__size):
            yield mark.value
            mark = mark.next

    def add_mark(self, value: int) -> None:
        """Add a mark at the end and close the circle."""
        mark = Mark(value)
        if self.__first is None:
            self.__first = mark
        else:
            self.__last.next = mark
        self.__last = mark
        self.__last.next = self.__first
        self.__size += 1
        self.__current = self.__first

    def find_mark(self, value: int) -> Mark:
        mark = self.__first
        for _ in range(self.__size):
            if mark.value == value:
                return mark
            mark = mark.next
        raise ValueError(f"{value} is not on the dial")

    def move(self, mark: Mark, steps: int) -> Mark:
        if self.__size == 0:
            raise ValueError("The dial is empty")
        for _ in range(steps % self.__size):
            mark = mark.next
        return mark

    def tick(self) -> bool:
        if self.__current is None:
            raise ValueError("The dial is empty")
        self.__current = self.__current.next
        return self.__current is self.__first

    def value_after(self, steps: int) -> int:
        """Value `steps` marks away from the cursor (negative goes backward)."""
        if self.__current is None:
            raise ValueError("The dial is empty")
        return self.move(self.__current, steps).value

    def set_to(self, value: int) -> None:
        self.__current = self.find_mark(value)
