from __future__ import annotations

import time

from robotin.domain.robot_state import RobotState
from robotin.infrastructure.display_gc9a01 import GC9A01DisplayPins, GC9A01DualDisplay
from robotin.infrastructure.eyes_renderer import EyesRenderer


def main() -> None:
    pins = GC9A01DisplayPins(
        dc_pin=25,
        rst_pin=24,
        left_cs_pin=8,
        right_cs_pin=7,
        bl_pin=18,
    )
    display = GC9A01DualDisplay(
        pins=pins,
        renderer=EyesRenderer(width=240, height=240),
        width=240,
        height=240,
        rotation=0,
        spi_hz=40_000_000,
    )

    sequence: list[RobotState | str] = [
        RobotState.IDLE,
        RobotState.LISTENING,
        RobotState.PROCESSING,
        RobotState.SPEAKING,
        "sleeping",
        RobotState.ERROR,
    ]

    while True:
        for item in sequence:
            if isinstance(item, RobotState):
                display.show_state(item)
            else:
                display.show_visual_state(item)
            time.sleep(1.0)


if __name__ == "__main__":
    main()
