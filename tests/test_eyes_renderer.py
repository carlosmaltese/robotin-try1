import pytest

from robotin.infrastructure.eyes_renderer import EyesRenderer


@pytest.mark.parametrize(
    "visual_state",
    ["idle", "listening", "thinking", "speaking", "sleeping", "error"],
)
def test_render_returns_240_square_rgb_image_for_each_visual_state(visual_state: str) -> None:
    renderer = EyesRenderer(width=240, height=240)

    image = renderer.render(visual_state)  # type: ignore[arg-type]

    assert image.mode == "RGB"
    assert image.size == (240, 240)
    assert image.getbbox() is not None


@pytest.mark.parametrize(
    "visual_state",
    ["idle", "listening", "thinking", "speaking", "sleeping", "error"],
)
def test_render_supports_left_and_right_eye_frames_that_differ(visual_state: str) -> None:
    renderer = EyesRenderer(width=240, height=240)

    left_image = renderer.render(visual_state, side="left")  # type: ignore[arg-type]
    right_image = renderer.render(visual_state, side="right")  # type: ignore[arg-type]

    if visual_state == "sleeping":
        assert left_image.size == (240, 240)
        assert right_image.size == (240, 240)
    else:
        assert left_image.tobytes() != right_image.tobytes()


def test_render_raises_for_unknown_visual_state() -> None:
    renderer = EyesRenderer()

    image = renderer.render("unknown")  # type: ignore[arg-type]

    assert image.mode == "RGB"
    assert image.size == (240, 240)


def test_render_raises_for_unknown_eye_side() -> None:
    renderer = EyesRenderer()

    with pytest.raises(ValueError, match="valid EyeSide"):
        renderer.render("idle", side="center")  # type: ignore[arg-type]


def test_expression_names_exposes_base_expressions() -> None:
    names = EyesRenderer.expression_names()

    assert set(names) == {
        "idle",
        "listening",
        "thinking",
        "speaking",
        "sleeping",
        "error",
        "happy",
        "sad",
        "confused",
        "surprised",
    }


def test_render_pair_is_deterministic_for_same_timestamp() -> None:
    renderer = EyesRenderer()

    left_a, right_a = renderer.render_pair("idle", timestamp=1.234)
    left_b, right_b = renderer.render_pair("idle", timestamp=1.234)

    assert left_a.tobytes() == left_b.tobytes()
    assert right_a.tobytes() == right_b.tobytes()


def test_renderer_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        EyesRenderer(width=0, height=240)

    with pytest.raises(ValueError, match="greater than 0"):
        EyesRenderer(width=240, height=-1)
