class Alarm:
    """Rings during the whole minute it is set for."""

    def __init__(self) -> None:
        self.__hours: int | None = None
        self.__minutes: int | None = None

    @property
    def is_set(self) -> bool:
        return self.__hours is not None

    def set(self, hours: int, minutes: int) -> None:
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError("Alarm time out of range")
        self.__hours = hours
        self.__minutes = minutes

    def cancel(self) -> None:
        self.__hours = None
        self.__minutes = None

    def is_ringing(self, hours: int, minutes: int) -> bool:
        return self.is_set and hours == self.__hours and minutes == self.__minutes

    def label(self) -> str:
        if not self.is_set:
            return "ALARM OFF"
        return f"ALARM {self.__hours:02d}:{self.__minutes:02d}"
