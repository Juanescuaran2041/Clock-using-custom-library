class ClockReading:
    """Everything the screen needs to show at one instant. Read-only."""

    def __init__(self, hours: int, minutes: int, seconds: int,
                 zone_name: str, alarm_label: str, alarm_ringing: bool) -> None:
        self.__hours = hours
        self.__minutes = minutes
        self.__seconds = seconds
        self.__zone_name = zone_name
        self.__alarm_label = alarm_label
        self.__alarm_ringing = alarm_ringing

    @property
    def hours(self) -> int:
        return self.__hours

    @property
    def minutes(self) -> int:
        return self.__minutes

    @property
    def seconds(self) -> int:
        return self.__seconds

    @property
    def zone_name(self) -> str:
        return self.__zone_name

    @property
    def alarm_label(self) -> str:
        return self.__alarm_label

    @property
    def alarm_ringing(self) -> bool:
        return self.__alarm_ringing

    def time_text(self) -> str:
        return f"{self.__hours:02d}:{self.__minutes:02d}:{self.__seconds:02d}"
