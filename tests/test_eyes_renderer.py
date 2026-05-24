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


def test_render_raises_for_unknown_visual_state() -> None:
    renderer = EyesRenderer()

    with pytest.raises(ValueError, match="Unsupported eye visual state"):
        renderer.render("unknown")  # type: ignore[arg-type]


def test_renderer_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        EyesRenderer(width=0, height=240)

    with pytest.raises(ValueError, match="greater than 0"):
        EyesRenderer(width=240, height=-1)
