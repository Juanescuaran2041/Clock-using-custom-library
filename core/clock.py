from core.dial import Dial

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24


class Clock:
    def __init__(self) -> None:
        self.__seconds_dial = self.__build_dial(SECONDS_PER_MINUTE)
        self.__minutes_dial = self.__build_dial(MINUTES_PER_HOUR)
        self.__hours_dial = self.__build_dial(HOURS_PER_DAY)

    @staticmethod
    def __build_dial(size: int) -> Dial:
        dial = Dial()
        for value in range(size):
            dial.add_mark(value)
        return dial

    @property
    def hours(self) -> int:
        return self.__hours_dial.current_value

    @property
    def minutes(self) -> int:
        return self.__minutes_dial.current_value

    @property
    def seconds(self) -> int:
        return self.__seconds_dial.current_value

    def hours_shifted(self, offset: int) -> int:
        """Hours as seen `offset` hours ahead (or behind, if negative)."""
        return self.__hours_dial.value_after(offset)

    def tick(self) -> None:
        if self.__seconds_dial.tick() and self.__minutes_dial.tick():
            self.__hours_dial.tick()

    def set_time(self, hours: int, minutes: int, seconds: int) -> None:
        self.__hours_dial.set_to(hours)
        self.__minutes_dial.set_to(minutes)
        self.__seconds_dial.set_to(seconds)

    def __str__(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
