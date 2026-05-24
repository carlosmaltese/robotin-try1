from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from robotin.infrastructure.eyes_renderer import EyeVisualState, EyesRenderer

STATES: tuple[EyeVisualState, ...] = (
    "idle",
    "listening",
    "thinking",
    "speaking",
    "sleeping",
    "error",
)


def compose_preview(left_image: Image.Image, right_image: Image.Image, state: EyeVisualState) -> Image.Image:
    margin = 16
    label_space = 30
    width = left_image.width + right_image.width + (margin * 3)
    height = max(left_image.height, right_image.height) + (margin * 2) + label_space

    canvas = Image.new("RGB", (width, height), (0, 0, 0))
    canvas.paste(left_image, (margin, margin))
    canvas.paste(right_image, (margin * 2 + left_image.width, margin))

    draw = ImageDraw.Draw(canvas)
    draw.text((margin, height - margin - 20), f"state: {state}", fill=(220, 220, 220))
    draw.text((margin, height - margin - 8), "left | right", fill=(160, 160, 160))
    return canvas


def generate_previews(output_dir: Path, *, make_gif: bool = True) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    renderer = EyesRenderer(width=240, height=240)

    generated: list[Path] = []
    gif_frames: list[Image.Image] = []

    for state in STATES:
        left_image, right_image = renderer.render_pair(state, timestamp=0.0)
        preview = compose_preview(left_image, right_image, state)

        output_path = output_dir / f"eyes_{state}.png"
        preview.save(output_path)
        generated.append(output_path)
        gif_frames.append(preview)

    if make_gif and gif_frames:
        gif_path = output_dir / "eyes_cycle.gif"
        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=700,
            loop=0,
        )
        generated.append(gif_path)

    return generated
