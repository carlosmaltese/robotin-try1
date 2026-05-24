from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from robotin.domain.robot_state import RobotState
from robotin.infrastructure.eyes_renderer import EyeVisualState, EyesRenderer
from robotin.interfaces.display import Display


@dataclass(frozen=True)
class GC9A01DisplayPins:
    dc_pin: int
    rst_pin: int
    left_cs_pin: int
    right_cs_pin: int
    bl_pin: int | None = None


class GC9A01DualDisplay(Display):
    _STATE_TO_VISUAL: dict[RobotState, EyeVisualState] = {
        RobotState.IDLE: "idle",
        RobotState.LISTENING: "listening",
        RobotState.PROCESSING: "thinking",
        RobotState.SPEAKING: "speaking",
        RobotState.ERROR: "error",
    }

    def __init__(
        self,
        *,
        pins: GC9A01DisplayPins,
        renderer: EyesRenderer | None = None,
        width: int = 240,
        height: int = 240,
        rotation: int = 0,
        spi_hz: int = 40_000_000,
        display_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._validate_pins(pins)
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be greater than 0")
        if spi_hz <= 0:
            raise ValueError("spi_hz must be greater than 0")

        self._pins = pins
        self._width = width
        self._height = height
        self._rotation = rotation
        self._spi_hz = spi_hz
        self._renderer = renderer or EyesRenderer(width=width, height=height)
        self._display_factory = display_factory

        self._left_display: Any | None = None
        self._right_display: Any | None = None

    def show_state(self, state: RobotState) -> None:
        if not isinstance(state, RobotState):
            raise TypeError("state must be a RobotState")

        visual_state = self.map_robot_state(state)
        self.show_visual_state(visual_state)

    def show_visual_state(self, visual_state: EyeVisualState) -> None:
        image = self._renderer.render(visual_state)
        self._ensure_initialized()
        self._left_display.display(image)
        self._right_display.display(image)

    @classmethod
    def map_robot_state(cls, state: RobotState) -> EyeVisualState:
        try:
            return cls._STATE_TO_VISUAL[state]
        except KeyError as exc:
            raise ValueError(f"No visual mapping defined for state: {state!r}") from exc

    def _ensure_initialized(self) -> None:
        if self._left_display is not None and self._right_display is not None:
            return

        factory = self._display_factory or self._build_default_factory()
        self._left_display = factory(cs=self._pins.left_cs_pin)
        self._right_display = factory(cs=self._pins.right_cs_pin)

    def _build_default_factory(self) -> Callable[..., Any]:
        # Lazy imports keep non-Raspberry environments testable.
        import board  # type: ignore[import-not-found]
        import digitalio  # type: ignore[import-not-found]
        import gc9a01  # type: ignore[import-not-found]
        import busio  # type: ignore[import-not-found]

        spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
        dc = digitalio.DigitalInOut(getattr(board, f"D{self._pins.dc_pin}"))
        rst = digitalio.DigitalInOut(getattr(board, f"D{self._pins.rst_pin}"))
        bl = (
            digitalio.DigitalInOut(getattr(board, f"D{self._pins.bl_pin}"))
            if self._pins.bl_pin is not None
            else None
        )

        def factory(*, cs: int) -> Any:
            cs_pin = digitalio.DigitalInOut(getattr(board, f"D{cs}"))
            return gc9a01.GC9A01(
                spi,
                cs=cs_pin,
                dc=dc,
                rst=rst,
                width=self._width,
                height=self._height,
                rotation=self._rotation,
                baudrate=self._spi_hz,
                backlight=bl,
            )

        return factory

    @staticmethod
    def _validate_pins(pins: GC9A01DisplayPins) -> None:
        candidates = [pins.dc_pin, pins.rst_pin, pins.left_cs_pin, pins.right_cs_pin]
        if pins.bl_pin is not None:
            candidates.append(pins.bl_pin)

        if any(pin < 0 for pin in candidates):
            raise ValueError("All pin values must be greater than or equal to 0")

        if pins.left_cs_pin == pins.right_cs_pin:
            raise ValueError("left_cs_pin and right_cs_pin must be different")
