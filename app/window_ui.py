import clocklib

from app.clock_app import ClockApp
from app.parsing import parse_time

SCREENSHOT_FILE = "output/clock.bmp"
MILLISECONDS_PER_TICK = 1000
CURSOR_BLINK_MS = 500
FRAME_DELAY_MS = 15

ENTER = 13
BACKSPACE = 8
ESCAPE = 27
FIRST_PRINTABLE = 32
MAX_LINE = 40

HELP = ("time HH:MM[:SS] | zone NAME | alarm HH:MM | clear | sync | bmp | "
        "zones: bogota, new york, london, madrid, tokyo")
TIME_FORMAT_HINT = "use the format HH:MM or HH:MM:SS, for example 14:30"


class WindowInterface:
    """A clock that runs by itself in a native window. Commands are typed into the window."""

    def __init__(self, app: ClockApp) -> None:
        self.__app = app
        self.__typed = ""
        self.__message = HELP

    def run(self) -> None:
        self.__sync_with_system()
        canvas = self.__app.canvas
        next_tick = clocklib.ticks_ms() + MILLISECONDS_PER_TICK
        while canvas.is_open:
            self.__handle_typing(canvas.events())
            now = clocklib.ticks_ms()
            while now >= next_tick:  # catches up if a frame was late
                self.__app.advance(1)
                next_tick += MILLISECONDS_PER_TICK
                if self.__app.reading().alarm_ringing:
                    clocklib.beep()
            show_cursor = (now // CURSOR_BLINK_MS) % 2 == 0
            if canvas.is_open:
                self.__app.render(self.__typed, self.__message, show_cursor)
            clocklib.sleep(FRAME_DELAY_MS)

    def __sync_with_system(self) -> None:
        """The machine is assumed to be in Bogota time, the home zone of the clock."""
        self.__app.set_time(*clocklib.system_time())

    def __handle_typing(self, codes: list[int]) -> None:
        for code in codes:
            if code == ENTER:
                self.__submit()
            elif code == BACKSPACE:
                self.__typed = self.__typed[:-1]
            elif code == ESCAPE:
                self.__typed = ""
            elif code >= FIRST_PRINTABLE and len(self.__typed) < MAX_LINE:
                self.__typed += chr(code)

    def __submit(self) -> None:
        line, self.__typed = self.__typed, ""
        if not line.strip():
            return
        try:
            self.__message = self.__execute(line)
        except ValueError as error:
            self.__message = f"Could not: {error}"

    def __execute(self, line: str) -> str:
        """Run one command. Returns what to tell the user, or raises ValueError."""
        command, _, argument = line.strip().partition(" ")
        command = command.lower()
        if command == "time":
            self.__app.set_time(*self.__parse(argument))
            return f"Time changed to {argument.strip()}."
        if command == "zone":
            return self.__change_zone(argument.strip())
        if command == "alarm":
            hours, minutes, _ = self.__parse(argument)
            self.__app.set_alarm(hours, minutes)
            return f"Alarm set for {hours:02d}:{minutes:02d}."
        if command == "clear":
            self.__app.cancel_alarm()
            return "Alarm cancelled."
        if command == "sync":
            self.__sync_with_system()
            return "Time taken from the system."
        if command == "bmp":
            self.__app.canvas.save_bmp(SCREENSHOT_FILE)
            return f"Saved to {SCREENSHOT_FILE}."
        if command in ("quit", "exit", "q"):
            self.__app.canvas.close()
            return ""
        raise ValueError(f"unknown command '{command}'. {HELP}")

    @staticmethod
    def __parse(text: str) -> tuple[int, int, int]:
        try:
            return parse_time(text)
        except ValueError:
            raise ValueError(TIME_FORMAT_HINT)

    def __change_zone(self, name: str) -> str:
        try:
            self.__app.select_zone(name)
        except ValueError:
            raise ValueError(f"unknown zone. Options: {', '.join(self.__app.zone_names)}")
        return f"Zone changed to {self.__app.reading().zone_name}."
