from __future__ import annotations

from pathlib import Path

from PIL import Image

from robotin.infrastructure.eyes_preview import STATES, compose_preview, generate_previews


def test_compose_preview_builds_expected_canvas_shape() -> None:
    left = Image.new("RGB", (240, 240), (10, 20, 30))
    right = Image.new("RGB", (240, 240), (40, 50, 60))

    canvas = compose_preview(left, right, "idle")

    assert canvas.mode == "RGB"
    assert canvas.size == (528, 302)


def test_generate_previews_writes_pngs_and_gif(tmp_path: Path) -> None:
    generated = generate_previews(tmp_path, make_gif=True)

    expected_pngs = {tmp_path / f"eyes_{state}.png" for state in STATES}
    expected_gif = tmp_path / "eyes_cycle.gif"

    assert expected_pngs.issubset(set(generated))
    assert expected_gif in generated
    assert all(path.exists() for path in generated)


def test_generate_previews_can_skip_gif(tmp_path: Path) -> None:
    generated = generate_previews(tmp_path, make_gif=False)

    assert all(path.suffix == ".png" for path in generated)
    assert not (tmp_path / "eyes_cycle.gif").exists()
