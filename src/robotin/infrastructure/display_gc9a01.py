from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import os
import time
from typing import Any

from robotin.domain.robot_state import RobotState
from robotin.infrastructure.eyes_renderer import EyeVisualState, EyesRenderer
from robotin.interfaces.display import Display


def _diag_enabled() -> bool:
    return os.getenv("ROBOTIN_DISPLAY_DIAG", "0") == "1"


def _diag(message: str) -> None:
    if _diag_enabled():
        print(f"[display_gc9a01] {message}")


@dataclass(frozen=True)
class GC9A01DisplayPins:
    left_dc_pin: int
    left_rst_pin: int
    left_cs_pin: int
    right_dc_pin: int
    right_rst_pin: int
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
        visual_state = self._map_robot_state_to_visual_state(state)
        self.show_visual_state(visual_state)

    def show_visual_state(self, visual_state: EyeVisualState) -> None:
        timestamp = time.monotonic()
        left_image, right_image = self._renderer.render_pair(visual_state, timestamp=timestamp)
        self._ensure_initialized()
        _diag(
            "write "
            f"state={visual_state} "
            f"left_display_id={id(self._left_display)} right_display_id={id(self._right_display)} "
            f"left_image_id={id(left_image)} right_image_id={id(right_image)}"
        )
        self._left_display.image(left_image)
        self._right_display.image(right_image)

    @classmethod
    def map_robot_state(cls, state: RobotState) -> EyeVisualState:
        return cls._map_robot_state_to_visual_state(state)

    @staticmethod
    def _map_robot_state_to_visual_state(state: object) -> EyeVisualState:
        raw = getattr(state, "value", str(state)).lower()
        mapping: dict[str, EyeVisualState] = {
            "idle": "idle",
            "listening": "listening",
            "processing": "thinking",
            "speaking": "speaking",
            "error": "error",
        }
        return mapping.get(raw, "idle")

    def _ensure_initialized(self) -> None:
        if self._left_display is not None and self._right_display is not None:
            _diag(
                "reuse displays "
                f"left_display_id={id(self._left_display)} right_display_id={id(self._right_display)}"
            )
            return

        _diag(f"module_path={__file__}")
        factory = self._display_factory or self._build_default_factory()
        _diag(
            "init left pins "
            f"cs={self._pins.left_cs_pin} dc={self._pins.left_dc_pin} rst={self._pins.left_rst_pin}"
        )
        self._left_display = factory(
            cs=self._pins.left_cs_pin,
            dc=self._pins.left_dc_pin,
            rst=self._pins.left_rst_pin,
        )
        _diag(
            "init right pins "
            f"cs={self._pins.right_cs_pin} dc={self._pins.right_dc_pin} rst={self._pins.right_rst_pin}"
        )
        self._right_display = factory(
            cs=self._pins.right_cs_pin,
            dc=self._pins.right_dc_pin,
            rst=self._pins.right_rst_pin,
        )
        _diag(
            "init complete "
            f"left_display_id={id(self._left_display)} right_display_id={id(self._right_display)}"
        )
        if self._left_display is self._right_display:
            _diag("WARNING left_display and right_display reference the same object")

    def _build_default_factory(self) -> Callable[..., Any]:
        # Lazy imports keep non-Raspberry environments testable.
        import board  # type: ignore[import-not-found]
        import digitalio  # type: ignore[import-not-found]
        from adafruit_rgb_display import gc9a01a  # type: ignore[import-not-found]
        import busio  # type: ignore[import-not-found]

        _diag(
            "imports "
            f"board={getattr(board, '__file__', '<builtin>')} "
            f"digitalio={getattr(digitalio, '__file__', '<builtin>')} "
            f"gc9a01a={getattr(gc9a01a, '__file__', '<builtin>')} "
            f"busio={getattr(busio, '__file__', '<builtin>')}"
        )

        spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)

        def factory(*, cs: int, dc: int, rst: int) -> Any:
            cs_pin = digitalio.DigitalInOut(getattr(board, f"D{cs}"))
            dc_pin = digitalio.DigitalInOut(getattr(board, f"D{dc}"))
            rst_pin = digitalio.DigitalInOut(getattr(board, f"D{rst}"))
            return gc9a01a.GC9A01A(
                spi,
                cs=cs_pin,
                dc=dc_pin,
                rst=rst_pin,
                width=self._width,
                height=self._height,
                rotation=self._rotation,
                baudrate=self._spi_hz,
            )

        return factory

    @staticmethod
    def _validate_pins(pins: GC9A01DisplayPins) -> None:
        control_pins = [
            pins.left_dc_pin,
            pins.left_rst_pin,
            pins.left_cs_pin,
            pins.right_dc_pin,
            pins.right_rst_pin,
            pins.right_cs_pin,
        ]
        candidates = list(control_pins)
        if pins.bl_pin is not None:
            candidates.append(pins.bl_pin)

        if any(pin < 0 for pin in candidates):
            raise ValueError("All pin values must be greater than or equal to 0")

        if len(set(control_pins)) != len(control_pins):
            raise ValueError("Each left/right control pin must be independent and unique")
