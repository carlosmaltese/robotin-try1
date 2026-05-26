from __future__ import annotations

import os
import time

from robotin.infrastructure.eyes_renderer import EyesRenderer


def _diag_enabled() -> bool:
    return os.getenv("ROBOTIN_DISPLAY_DIAG", "0") == "1"


def _diag(message: str) -> None:
    if _diag_enabled():
        print(f"[demo_eyes_gc9a01] {message}")


def _create_dual_displays():
    # Lazy Raspberry-specific imports to keep Windows-safe module import.
    import board  # type: ignore[import-not-found]
    import busio  # type: ignore[import-not-found]
    import digitalio  # type: ignore[import-not-found]
    from adafruit_rgb_display import gc9a01a  # type: ignore[import-not-found]

    _diag(f"module_path={__file__}")
    _diag(
        "imports "
        f"board={getattr(board, '__file__', '<builtin>')} "
        f"digitalio={getattr(digitalio, '__file__', '<builtin>')} "
        f"gc9a01a={getattr(gc9a01a, '__file__', '<builtin>')} "
        f"busio={getattr(busio, '__file__', '<builtin>')}"
    )

    spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
    _diag("init left pins cs=8 dc=25 rst=24")

    left_display = gc9a01a.GC9A01A(
        spi,
        cs=digitalio.DigitalInOut(getattr(board, "D8")),
        dc=digitalio.DigitalInOut(getattr(board, "D25")),
        rst=digitalio.DigitalInOut(getattr(board, "D24")),
        width=240,
        height=240,
        rotation=0,
        baudrate=40_000_000,
    )
    _diag("init right pins cs=7 dc=23 rst=22")
    right_display = gc9a01a.GC9A01A(
        spi,
        cs=digitalio.DigitalInOut(getattr(board, "D7")),
        dc=digitalio.DigitalInOut(getattr(board, "D23")),
        rst=digitalio.DigitalInOut(getattr(board, "D22")),
        width=240,
        height=240,
        rotation=0,
        baudrate=40_000_000,
    )
    _diag(
        "init complete "
        f"left_display_id={id(left_display)} right_display_id={id(right_display)}"
    )
    if left_display is right_display:
        _diag("WARNING left_display and right_display reference the same object")
    return left_display, right_display


def main() -> None:
    left_display, right_display = _create_dual_displays()
    renderer = EyesRenderer(size=240)

    states = [
        "idle",
        "listening",
        "thinking",
        "speaking",
        "sleeping",
        "error",
    ]

    while True:
        for state in states:
            start = time.monotonic()
            while time.monotonic() - start < 3.0:
                now = time.monotonic()
                left_image, right_image = renderer.render_pair(state, timestamp=now, animate=True)
                _diag(
                    "write "
                    f"state={state} "
                    f"left_display_id={id(left_display)} right_display_id={id(right_display)} "
                    f"left_image_id={id(left_image)} right_image_id={id(right_image)}"
                )
                left_display.image(left_image)
                right_display.image(right_image)
                time.sleep(0.05)


if __name__ == "__main__":
    main()
