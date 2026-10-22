from app.clock_app import ClockApp
from app.window_ui import WindowInterface


def main() -> None:
    WindowInterface(ClockApp()).run()


if __name__ == "__main__":
    main()
