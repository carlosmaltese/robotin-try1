from __future__ import annotations

import time

from robotin.infrastructure.eyes_renderer import EyesRenderer


def _create_dual_displays():
    # Lazy Raspberry-specific imports to keep Windows-safe module import.
    import board  # type: ignore[import-not-found]
    import busio  # type: ignore[import-not-found]
    import digitalio  # type: ignore[import-not-found]
    from adafruit_rgb_display import gc9a01a  # type: ignore[import-not-found]

    spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)

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
                left_display.image(left_image)
                right_display.image(right_image)
                time.sleep(0.05)


if __name__ == "__main__":
    main()
