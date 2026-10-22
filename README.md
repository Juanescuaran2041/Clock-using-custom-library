# Clock using a custom C library

An analog and digital clock in a **real window**. Python imports nothing from the standard library or third parties: the only external import is `clocklib`, a library written in C for this project (`native/clocklib.c`) that Python imports like any other module.

The central data structure is a **circular linked list** (`Mark` / `Dial`), with three chained rings (seconds, minutes, hours) that advance like gears.

## Build and run

Requires Windows, Python 3.10+ (64-bit) and MinGW gcc from MSYS2 (`C:\msys64\ucrt64\bin\gcc.exe`).

```text
powershell -ExecutionPolicy Bypass -File build.ps1   # builds clocklib.pyd
python main.py
```

## What `clocklib` provides

Without imports, Python cannot open a window, read the time, wait or make a sound. The C library offers only that:

| Function | Purpose |
|---|---|
| `Window(title, width, height)` | Win32 window with a drawing surface (`fill`, `line`, `circle`, `fill_circle`, `rect`, `text`, `present`, `poll`, `save_bmp`, `close`) |
| `sin`, `cos` | Trigonometry |
| `system_time()` | Local machine time `(h, m, s)` |
| `ticks_ms()`, `sleep(ms)` | Measure and wait time |
| `beep()` | Alarm sound |

## Usage

On start the clock takes the system time (assumed to be Bogota time) and runs by itself. Commands are typed in the bar at the bottom of the window and sent with Enter (`Esc` clears the line):

| Command | What it does |
|---|---|
| `time HH:MM[:SS]` | Sets the time (Bogota time) |
| `zone NAME` | `BOGOTA`, `NEW YORK`, `LONDON`, `MADRID`, `TOKYO` |
| `alarm HH:MM` | Sets the alarm in the zone being shown |
| `clear` | Cancels the alarm |
| `sync` | Takes the system time again |
| `bmp` | Saves a screenshot to `output/clock.bmp` |
| `quit` | Exits |

When the alarm rings the border turns red, `RINGING` appears and the system alert sound plays.

## Structure

```text
main.py                 entry point
build.ps1               builds clocklib.pyd
native/clocklib.c       the C library
app/
  clock_app.py          joins the clock logic with the window
  window_ui.py          main loop, keyboard and commands
  parsing.py            reads "HH:MM[:SS]"
core/
  dial.py               Mark and Dial: the circular linked list
  clock.py              three chained Dials
  time_zone.py, alarm.py, clock_reading.py
graphics/
  canvas.py             window surface (wraps clocklib.Window)
  shapes.py             Line, Circle, FilledCircle, Rectangle, Text
  hands.py              clock hands
  clock_view.py         face, digital display and command bar
  math_utils.py, palette.py, scaling.py
```
