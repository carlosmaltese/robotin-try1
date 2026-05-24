from __future__ import annotations

from pathlib import Path

from robotin.infrastructure.eyes_renderer import EyesRenderer

OUTPUT_DIR = Path("previews")


def generate_windows_previews() -> list[Path]:
    OUTPUT_DIR.mkdir(exist_ok=True)

    renderer = EyesRenderer()
    states = [
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
    ]

    generated: list[Path] = []
    for state in states:
        image = renderer.render_preview_pair(state, timestamp=1.0, animate=False)
        out = OUTPUT_DIR / f"eyes_{state}.png"
        image.save(out)
        generated.append(out)
    return generated


def main() -> None:
    generated = generate_windows_previews()
    print(f"Generated previews in: {OUTPUT_DIR.resolve()}")
    for file_path in generated:
        print(f" - {file_path}")


if __name__ == "__main__":
    main()
