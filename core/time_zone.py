class TimeZone:
    def __init__(self, name: str, utc_offset: int) -> None:
        self.__name = name
        self.__utc_offset = utc_offset

    @property
    def name(self) -> str:
        return self.__name

    @property
    def utc_offset(self) -> int:
        return self.__utc_offset


# Offsets valid in October 2026 (daylight saving time included where it applies).
ZONES = (
    TimeZone("BOGOTA", -5),
    TimeZone("NEW YORK", -4),
    TimeZone("LONDON", 1),
    TimeZone("MADRID", 2),
    TimeZone("TOKYO", 9),
)


def find_zone(name: str) -> TimeZone | None:
    """Return the first zone whose name starts with the given text."""
    name = name.strip().upper()
    for zone in ZONES:
        if name and zone.name.startswith(name):
            return zone
    return None
