from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PIL import Image, ImageDraw

EyeVisualState = Literal[
    "idle",
    "listening",
    "thinking",
    "speaking",
    "sleeping",
    "error",
]


@dataclass(frozen=True)
class EyesRenderer:
    width: int = 240
    height: int = 240

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be greater than 0")

    def render(self, state: EyeVisualState) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        if state == "idle":
            self._draw_idle(draw)
        elif state == "listening":
            self._draw_listening(draw)
        elif state == "thinking":
            self._draw_thinking(draw)
        elif state == "speaking":
            self._draw_speaking(draw)
        elif state == "sleeping":
            self._draw_sleeping(draw)
        elif state == "error":
            self._draw_error(draw)
        else:
            raise ValueError(f"Unsupported eye visual state: {state!r}")

        return image

    def _draw_idle(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw_face_outline(draw, (40, 200, 255))
        self._draw_eye(draw, center=(80, 120), radius=40, color=(255, 255, 255), pupil=(0, 0, 0))
        self._draw_eye(draw, center=(160, 120), radius=40, color=(255, 255, 255), pupil=(0, 0, 0))

    def _draw_listening(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw_face_outline(draw, (40, 255, 120))
        self._draw_eye(draw, center=(80, 120), radius=42, color=(230, 255, 230), pupil=(20, 120, 20))
        self._draw_eye(draw, center=(160, 120), radius=42, color=(230, 255, 230), pupil=(20, 120, 20))
        draw.arc((26, 26, 214, 214), start=220, end=320, fill=(40, 255, 120), width=6)

    def _draw_thinking(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw_face_outline(draw, (180, 180, 255))
        self._draw_eye(draw, center=(80, 120), radius=38, color=(255, 255, 255), pupil=(90, 90, 170))
        self._draw_eye(draw, center=(160, 120), radius=38, color=(255, 255, 255), pupil=(90, 90, 170))
        for index, radius in enumerate((8, 12, 16)):
            x = 70 + (index * 24)
            y = 56 - (index * 6)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(180, 180, 255), width=2)

    def _draw_speaking(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw_face_outline(draw, (255, 220, 80))
        self._draw_eye(draw, center=(80, 110), radius=36, color=(255, 255, 255), pupil=(120, 90, 0))
        self._draw_eye(draw, center=(160, 110), radius=36, color=(255, 255, 255), pupil=(120, 90, 0))
        draw.arc((70, 130, 170, 210), start=20, end=160, fill=(255, 220, 80), width=8)

    def _draw_sleeping(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw_face_outline(draw, (110, 130, 255))
        draw.line((48, 112, 112, 112), fill=(220, 230, 255), width=8)
        draw.line((128, 112, 192, 112), fill=(220, 230, 255), width=8)
        draw.text((148, 56), "Z", fill=(180, 200, 255))
        draw.text((164, 38), "Z", fill=(180, 200, 255))

    def _draw_error(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw_face_outline(draw, (255, 70, 70))
        draw.line((56, 88, 104, 136), fill=(255, 200, 200), width=7)
        draw.line((104, 88, 56, 136), fill=(255, 200, 200), width=7)
        draw.line((136, 88, 184, 136), fill=(255, 200, 200), width=7)
        draw.line((184, 88, 136, 136), fill=(255, 200, 200), width=7)
        draw.arc((70, 148, 170, 212), start=200, end=340, fill=(255, 70, 70), width=8)

    def _draw_face_outline(self, draw: ImageDraw.ImageDraw, color: tuple[int, int, int]) -> None:
        draw.ellipse((8, 8, self.width - 8, self.height - 8), outline=color, width=8)

    @staticmethod
    def _draw_eye(
        draw: ImageDraw.ImageDraw,
        center: tuple[int, int],
        radius: int,
        color: tuple[int, int, int],
        pupil: tuple[int, int, int],
    ) -> None:
        cx, cy = center
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
        pupil_radius = max(10, radius // 3)
        draw.ellipse(
            (cx - pupil_radius, cy - pupil_radius, cx + pupil_radius, cy + pupil_radius),
            fill=pupil,
        )
