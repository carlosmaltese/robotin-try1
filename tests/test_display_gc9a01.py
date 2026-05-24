from __future__ import annotations

from unittest.mock import patch

import pytest
from PIL import Image

from robotin.domain.robot_state import RobotState
from robotin.infrastructure.display_gc9a01 import GC9A01DisplayPins, GC9A01DualDisplay
from robotin.infrastructure.eyes_renderer import EyesRenderer


class _FakePhysicalDisplay:
    def __init__(self) -> None:
        self.images = []

    def image(self, image) -> None:
        self.images.append(image)

    def display(self, image) -> None:
        self.images.append(image)


class _RendererThatRequiresPair(EyesRenderer):
    def render(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("single-frame render path should not be used")

    def render_pair(self, state, *, timestamp, phase=None):  # type: ignore[no-untyped-def]
        _ = (state, timestamp, phase)
        return (
            Image.new("RGB", (self.size, self.size), (1, 2, 3)),
            Image.new("RGB", (self.size, self.size), (4, 5, 6)),
        )


def _build_adapter(displays: tuple[_FakePhysicalDisplay, _FakePhysicalDisplay]) -> GC9A01DualDisplay:
    index = 0
    calls: list[dict[str, int]] = []

    def factory(*, cs: int, dc: int, rst: int):
        nonlocal index
        calls.append({"cs": cs, "dc": dc, "rst": rst})
        selected = displays[index]
        index += 1
        return selected

    adapter = GC9A01DualDisplay(
        pins=GC9A01DisplayPins(
            left_dc_pin=25,
            left_rst_pin=24,
            left_cs_pin=8,
            right_dc_pin=23,
            right_rst_pin=22,
            right_cs_pin=7,
            bl_pin=18,
        ),
        renderer=EyesRenderer(width=240, height=240),
        display_factory=factory,
    )
    adapter._factory_calls = calls  # type: ignore[attr-defined]
    return adapter


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

    assert len(left.images) == 1
    assert len(right.images) == 1
    assert left.images[0].size == (240, 240)
    assert right.images[0].size == (240, 240)
    assert left.images[0].tobytes() != right.images[0].tobytes()
    assert adapter._factory_calls == [  # type: ignore[attr-defined]
        {"cs": 8, "dc": 25, "rst": 24},
        {"cs": 7, "dc": 23, "rst": 22},
    ]


def test_show_visual_state_supports_sleeping_for_demo() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()
    adapter = _build_adapter((left, right))

    adapter.show_visual_state("sleeping")

    assert len(left.images) == 1
    assert len(right.images) == 1


def test_show_visual_state_uses_shared_timestamp_for_left_and_right_rendering() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()
    adapter = _build_adapter((left, right))

    with patch("robotin.infrastructure.display_gc9a01.time.monotonic", return_value=12.34):
        adapter.show_visual_state("idle")

    assert len(left.images) == 1
    assert len(right.images) == 1
    assert left.images[0].size == (240, 240)
    assert right.images[0].size == (240, 240)


def test_show_visual_state_uses_render_pair_instead_of_single_render() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()

    index = 0

    def factory(*, cs: int, dc: int, rst: int):
        nonlocal index
        _ = (cs, dc, rst)
        selected = (left, right)[index]
        index += 1
        return selected

    adapter = GC9A01DualDisplay(
        pins=GC9A01DisplayPins(
            left_dc_pin=25,
            left_rst_pin=24,
            left_cs_pin=8,
            right_dc_pin=23,
            right_rst_pin=22,
            right_cs_pin=7,
        ),
        renderer=_RendererThatRequiresPair(width=240, height=240),
        display_factory=factory,
    )

    adapter.show_visual_state("idle")

    assert len(left.images) == 1
    assert len(right.images) == 1


def test_show_state_rejects_non_robot_state_value() -> None:
    left = _FakePhysicalDisplay()
    right = _FakePhysicalDisplay()
    adapter = _build_adapter((left, right))

    with pytest.raises(TypeError, match="RobotState"):
        adapter.show_state("idle")  # type: ignore[arg-type]


def test_adapter_rejects_duplicate_chip_select_pins() -> None:
    with pytest.raises(ValueError, match="independent and unique"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(
                left_dc_pin=25,
                left_rst_pin=24,
                left_cs_pin=8,
                right_dc_pin=23,
                right_rst_pin=22,
                right_cs_pin=8,
            ),
        )


def test_adapter_rejects_duplicate_dc_or_rst_pins() -> None:
    with pytest.raises(ValueError, match="independent and unique"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(
                left_dc_pin=25,
                left_rst_pin=24,
                left_cs_pin=8,
                right_dc_pin=25,
                right_rst_pin=22,
                right_cs_pin=7,
            ),
        )


def test_adapter_rejects_non_positive_dimensions_and_spi_rate() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(
                left_dc_pin=25,
                left_rst_pin=24,
                left_cs_pin=8,
                right_dc_pin=23,
                right_rst_pin=22,
                right_cs_pin=7,
            ),
            width=0,
        )

    with pytest.raises(ValueError, match="greater than 0"):
        GC9A01DualDisplay(
            pins=GC9A01DisplayPins(
                left_dc_pin=25,
                left_rst_pin=24,
                left_cs_pin=8,
                right_dc_pin=23,
                right_rst_pin=22,
                right_cs_pin=7,
            ),
            spi_hz=0,
        )
