from __future__ import annotations

import pytest

from robotin.domain.robot_state import RobotState
from robotin.infrastructure.display_gc9a01 import GC9A01DisplayPins, GC9A01DualDisplay
from robotin.infrastructure.eyes_renderer import EyesRenderer


class _FakePhysicalDisplay:
    def __init__(self) -> None:
        self.frames = []

    def display(self, image) -> None:
        self.frames.append(image)


def _build_adapter(displays: tuple[_FakePhysicalDisplay, _FakePhysicalDisplay]) -> GC9A01DualDisplay:
    index = 0

    def factory(*, cs: int):
        nonlocal index
        _ = cs
        selected = displays[index]
        index += 1
        return selected

    return GC9A01DualDisplay(
        pins=GC9A01DisplayPins(dc_pin=25, rst_pin=24, left_cs_pin=8, right_cs_pin=7, bl_pin=18),
        renderer=EyesRenderer(width=240, height=240),
        display_factory=factory,
    )


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (RobotState.IDLE, "idle"),
        (RobotState.LISTENING, "listening"),
        (RobotState.PROCESSING, "thinking"),
        (RobotState.SPEAKING, "speaking"),
        (RobotState.ERROR, "error"),
    ],
)
def test_map_robot_state_matches_expected_visual_state(state: RobotState, expected: str) -> None:
    assert GC9A01DualDisplay.map_robot_state(state) == expected


def test_show_state_renders_and_sends_frame_to_both_displays() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()
    adapter = _build_adapter((left, right))

    adapter.show_state(RobotState.IDLE)

    assert len(left.frames) == 1
    assert len(right.frames) == 1
    assert left.frames[0].size == (240, 240)
    assert right.frames[0].size == (240, 240)


def test_show_visual_state_supports_sleeping_for_demo() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()
    adapter = _build_adapter((left, right))

    adapter.show_visual_state("sleeping")

    assert len(left.frames) == 1
    assert len(right.frames) == 1


def test_show_state_rejects_non_robot_state_value() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()
    adapter = _build_adapter((left, right))

    with pytest.raises(TypeError, match="RobotState"):
        adapter.show_state("idle")  # type: ignore[arg-type]


def test_adapter_rejects_duplicate_chip_select_pins() -> None:
    with pytest.raises(ValueError, match="must be different"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(dc_pin=25, rst_pin=24, left_cs_pin=8, right_cs_pin=8),
        )


def test_adapter_rejects_non_positive_dimensions_and_spi_rate() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(dc_pin=25, rst_pin=24, left_cs_pin=8, right_cs_pin=7),
            width=0,
        )

    with pytest.raises(ValueError, match="greater than 0"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(dc_pin=25, rst_pin=24, left_cs_pin=8, right_cs_pin=7),
            spi_hz=0,
        )
