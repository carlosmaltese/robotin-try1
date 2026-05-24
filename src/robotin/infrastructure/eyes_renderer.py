from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from PIL import Image, ImageChops, ImageDraw, ImageFilter

RGB = Tuple[int, int, int]


class EyeSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class EyeVisualState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    SLEEPING = "sleeping"
    ERROR = "error"
    HAPPY = "happy"
    SAD = "sad"
    CONFUSED = "confused"
    SURPRISED = "surprised"


@dataclass(frozen=True)
class EyeExpression:
    eye_width: int
    eye_height: int
    eye_center_x: int
    eye_center_y: int
    pupil_radius: int
    pupil_offset_x: int
    pupil_offset_y: int
    eyelid_top: float
    eyelid_bottom: float
    eyebrow_y: int
    eyebrow_angle: float
    eyebrow_curve: float
    eyebrow_width: int
    eyebrow_thickness: int
    eye_color: RGB = (245, 248, 255)
    pupil_color: RGB = (8, 14, 28)
    highlight_color: RGB = (255, 255, 255)
    eyebrow_color: RGB = (210, 230, 255)
    background_color: RGB = (0, 0, 0)


class EyesRenderer:
    def __init__(
        self,
        size: int = 240,
        background_color: RGB = (0, 0, 0),
        subtle_outer_glow: bool = True,
        **legacy_kwargs: object,
    ) -> None:
        if "width" in legacy_kwargs and isinstance(legacy_kwargs["width"], int):
            size = int(legacy_kwargs["width"])
        if "height" in legacy_kwargs and isinstance(legacy_kwargs["height"], int):
            size = min(size, int(legacy_kwargs["height"]))
        if size <= 0:
            raise ValueError("size must be greater than 0")
        self.size = size
        self.background_color = background_color
        self.subtle_outer_glow = subtle_outer_glow

    def render_pair(
        self,
        state: str | EyeVisualState,
        timestamp: float = 0.0,
        animate: bool = True,
    ) -> tuple[Image.Image, Image.Image]:
        visual_state = self._normalize_state(state)
        left = self.render_eye(visual_state, EyeSide.LEFT, timestamp=timestamp, animate=animate)
        right = self.render_eye(visual_state, EyeSide.RIGHT, timestamp=timestamp, animate=animate)
        return left, right

    def render_eye(
        self,
        state: str | EyeVisualState,
        side: EyeSide | str,
        timestamp: float = 0.0,
        animate: bool = True,
    ) -> Image.Image:
        visual_state = self._normalize_state(state)
        eye_side = EyeSide(side)
        expression = self._expression_for(visual_state, eye_side, timestamp, animate)

        image = Image.new("RGB", (self.size, self.size), expression.background_color)
        draw = ImageDraw.Draw(image)
        if self.subtle_outer_glow:
            self._draw_subtle_screen_glow(image, visual_state)
        self._draw_eyebrow(draw, expression)
        self._draw_eye_shape(draw, expression)
        self._draw_pupil(draw, expression)
        return image

    def render_preview_pair(
        self,
        state: str | EyeVisualState,
        timestamp: float = 0.0,
        animate: bool = False,
        gap: int = 24,
        label: bool = True,
    ) -> Image.Image:
        left, right = self.render_pair(state, timestamp=timestamp, animate=animate)
        label_height = 28 if label else 0
        width = self.size * 2 + gap
        height = self.size + label_height

        preview = Image.new("RGB", (width, height), self.background_color)
        preview.paste(left, (0, 0))
        preview.paste(right, (self.size + gap, 0))

        if label:
            draw = ImageDraw.Draw(preview)
            draw.text((4, self.size + 4), f"state: {self._normalize_state(state).value}", fill=(190, 190, 190))
            draw.text((4, self.size + 16), "left | right", fill=(150, 150, 150))
        return preview

    # compatibility with previous API
    def render(self, state: str | EyeVisualState, side: str | EyeSide = "left", timestamp: float | None = None, phase: float | None = None) -> Image.Image:
        t = timestamp if timestamp is not None else (phase if phase is not None else 0.0)
        return self.render_eye(state, side, timestamp=t, animate=False)

    @staticmethod
    def expression_names() -> tuple[str, ...]:
        return tuple(s.value for s in EyeVisualState)

    def _normalize_state(self, state: str | EyeVisualState) -> EyeVisualState:
        if isinstance(state, EyeVisualState):
            return state
        raw = str(state).lower()
        aliases = {
            "processing": EyeVisualState.THINKING,
            "think": EyeVisualState.THINKING,
            "talking": EyeVisualState.SPEAKING,
            "speak": EyeVisualState.SPEAKING,
            "asleep": EyeVisualState.SLEEPING,
            "sleep": EyeVisualState.SLEEPING,
            "wake": EyeVisualState.LISTENING,
            "wake_detected": EyeVisualState.LISTENING,
        }
        if raw in aliases:
            return aliases[raw]
        try:
            return EyeVisualState(raw)
        except ValueError:
            return EyeVisualState.IDLE

    def _expression_for(self, state: EyeVisualState, side: EyeSide, timestamp: float, animate: bool) -> EyeExpression:
        center_x = 120
        center_y = 138
        eye_width = 128
        eye_height = 86
        pupil_radius = 22
        pupil_offset_x = 0
        pupil_offset_y = 0
        eyebrow_y = 62
        eyebrow_angle = 0.0
        eyebrow_curve = -12.0
        eyebrow_width = 112
        eyebrow_thickness = 8
        eyelid_top = 0.0
        eyelid_bottom = 0.0

        inward = 9 if side == EyeSide.LEFT else -9
        pupil_offset_x += inward

        if state == EyeVisualState.IDLE:
            eyebrow_y = 58
            eyebrow_angle = -4 if side == EyeSide.LEFT else 4
            eyebrow_curve = -14
        elif state == EyeVisualState.LISTENING:
            eye_width = 136
            eye_height = 94
            pupil_radius = 21
            eyebrow_y = 48
            eyebrow_angle = -2 if side == EyeSide.LEFT else 2
            eyebrow_curve = -18
            pupil_offset_y = -2
        elif state == EyeVisualState.THINKING:
            pupil_offset_y = -18
            pupil_offset_x += -10 if side == EyeSide.LEFT else 10
            eyelid_top = 0.10
            eyebrow_y = 54
            eyebrow_angle = -16 if side == EyeSide.LEFT else 16
            eyebrow_curve = -8
        elif state == EyeVisualState.SPEAKING:
            pupil_offset_x += int(4 * math.sin(timestamp * 8.0)) if animate else 0
            pupil_offset_y += int(3 * math.sin(timestamp * 6.5)) if animate else 0
            eyebrow_y = 54 + (int(2 * math.sin(timestamp * 7.0)) if animate else 0)
            eyebrow_angle = -4 if side == EyeSide.LEFT else 4
            eyebrow_curve = -14
        elif state == EyeVisualState.SLEEPING:
            eye_width = 124
            eye_height = 14
            pupil_radius = 0
            eyelid_top = 0.92
            eyebrow_y = 70
            eyebrow_curve = 4
            eyebrow_width = 102
            eyebrow_thickness = 7
        elif state == EyeVisualState.ERROR:
            eye_width = 112
            eye_height = 82
            pupil_radius = 18
            pupil_offset_y = 5
            eyebrow_y = 56
            eyebrow_angle = 22 if side == EyeSide.LEFT else -22
            eyebrow_curve = -5
            eyelid_top = 0.04
        elif state == EyeVisualState.HAPPY:
            eye_width = 130
            eye_height = 66
            pupil_radius = 18
            pupil_offset_y = -3
            eyebrow_y = 52
            eyebrow_angle = -5 if side == EyeSide.LEFT else 5
            eyebrow_curve = -20
            eyelid_bottom = 0.12
        elif state == EyeVisualState.SAD:
            eye_width = 118
            eye_height = 74
            pupil_radius = 18
            pupil_offset_y = 8
            eyebrow_y = 58
            eyebrow_angle = 18 if side == EyeSide.LEFT else -18
            eyebrow_curve = 2
            eyelid_top = 0.12
        elif state == EyeVisualState.CONFUSED:
            pupil_offset_x += -6 if side == EyeSide.LEFT else 7
            pupil_offset_y = -5 if side == EyeSide.LEFT else 4
            eyebrow_y = 50 if side == EyeSide.LEFT else 64
            eyebrow_angle = -18 if side == EyeSide.LEFT else 8
            eyebrow_curve = -8
            eyelid_top = 0.08 if side == EyeSide.RIGHT else 0.0
        elif state == EyeVisualState.SURPRISED:
            eye_width = 136
            eye_height = 106
            pupil_radius = 19
            pupil_offset_y = -3
            eyebrow_y = 42
            eyebrow_angle = -2 if side == EyeSide.LEFT else 2
            eyebrow_curve = -22

        if animate and state not in {EyeVisualState.SLEEPING}:
            blink = self._blink_amount(timestamp)
            if blink > 0:
                eyelid_top = max(eyelid_top, blink)
                eyelid_bottom = max(eyelid_bottom, blink * 0.55)
            drift_x, drift_y = self._idle_drift(timestamp, state)
            pupil_offset_x += drift_x
            pupil_offset_y += drift_y

        return EyeExpression(
            eye_width=eye_width,
            eye_height=eye_height,
            eye_center_x=center_x,
            eye_center_y=center_y,
            pupil_radius=pupil_radius,
            pupil_offset_x=pupil_offset_x,
            pupil_offset_y=pupil_offset_y,
            eyelid_top=eyelid_top,
            eyelid_bottom=eyelid_bottom,
            eyebrow_y=eyebrow_y,
            eyebrow_angle=eyebrow_angle,
            eyebrow_curve=eyebrow_curve,
            eyebrow_width=eyebrow_width,
            eyebrow_thickness=eyebrow_thickness,
        )

    def _draw_subtle_screen_glow(self, image: Image.Image, state: EyeVisualState) -> None:
        color_by_state: dict[EyeVisualState, RGB] = {
            EyeVisualState.ERROR: (40, 5, 12),
            EyeVisualState.LISTENING: (4, 18, 32),
            EyeVisualState.THINKING: (10, 8, 30),
            EyeVisualState.SPEAKING: (4, 20, 18),
            EyeVisualState.SLEEPING: (2, 6, 18),
        }
        glow_color = color_by_state.get(state, (4, 10, 18))
        overlay = Image.new("RGB", image.size, (0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.ellipse((16, 16, self.size - 16, self.size - 16), outline=glow_color, width=5)
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=8))
        blended = Image.blend(image, overlay, alpha=0.25)
        image.paste(blended)

    def _draw_eye_shape(self, draw: ImageDraw.ImageDraw, expression: EyeExpression) -> None:
        cx = expression.eye_center_x
        cy = expression.eye_center_y
        w = expression.eye_width
        h = expression.eye_height
        bbox = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)

        if h <= 18:
            y = cy
            self._draw_curve(draw, (cx - w // 2, y), (cx, y + 10), (cx + w // 2, y), fill=expression.eye_color, width=8)
            return

        draw.ellipse(bbox, fill=expression.eye_color)
        draw.ellipse(bbox, outline=(35, 40, 50), width=3)

        if expression.eyelid_top > 0:
            lid_h = int((h + 34) * expression.eyelid_top)
            draw.rounded_rectangle((cx - w // 2 - 8, cy - h // 2 - 12, cx + w // 2 + 8, cy - h // 2 - 12 + lid_h), radius=22, fill=expression.background_color)

        if expression.eyelid_bottom > 0:
            lid_h = int((h + 30) * expression.eyelid_bottom)
            draw.rounded_rectangle((cx - w // 2 - 8, cy + h // 2 + 12 - lid_h, cx + w // 2 + 8, cy + h // 2 + 12), radius=22, fill=expression.background_color)

    def _draw_pupil(self, draw: ImageDraw.ImageDraw, expression: EyeExpression) -> None:
        if expression.pupil_radius <= 0 or expression.eye_height <= 18:
            return
        px = expression.eye_center_x + expression.pupil_offset_x
        py = expression.eye_center_y + expression.pupil_offset_y
        r = expression.pupil_radius
        draw.ellipse((px - r, py - r, px + r, py + r), fill=expression.pupil_color)

        inner_r = max(5, int(r * 0.45))
        draw.ellipse((px - inner_r, py - inner_r, px + inner_r, py + inner_r), outline=(78, 84, 180), width=5)

        highlight_r = max(4, int(r * 0.28))
        hx = px + int(r * 0.38)
        hy = py - int(r * 0.38)
        draw.ellipse((hx - highlight_r, hy - highlight_r, hx + highlight_r, hy + highlight_r), fill=expression.highlight_color)

    def _draw_eyebrow(self, draw: ImageDraw.ImageDraw, expression: EyeExpression) -> None:
        cx = expression.eye_center_x
        y = expression.eyebrow_y
        half = expression.eyebrow_width // 2
        angle_rad = math.radians(expression.eyebrow_angle)
        dx = half * math.cos(angle_rad)
        dy = half * math.sin(angle_rad)
        start = (int(cx - dx), int(y - dy))
        end = (int(cx + dx), int(y + dy))
        control = (cx, int(y + expression.eyebrow_curve))
        self._draw_curve(draw, start, control, end, fill=expression.eyebrow_color, width=expression.eyebrow_thickness)

    def _draw_curve(
        self,
        draw: ImageDraw.ImageDraw,
        start: tuple[int, int],
        control: tuple[int, int],
        end: tuple[int, int],
        fill: RGB,
        width: int,
        steps: int = 28,
    ) -> None:
        points: list[tuple[int, int]] = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
            y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
            points.append((int(x), int(y)))
        draw.line(points, fill=fill, width=width, joint="curve")
        radius = max(2, width // 2)
        for point in (points[0], points[-1]):
            draw.ellipse((point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius), fill=fill)

    def _blink_amount(self, timestamp: float) -> float:
        cycle = 4.8
        phase = timestamp % cycle
        if 4.35 <= phase <= 4.55:
            local = (phase - 4.35) / 0.20
            return math.sin(local * math.pi)
        if 4.68 <= phase <= 4.82:
            local = (phase - 4.68) / 0.14
            return 0.75 * math.sin(local * math.pi)
        return 0.0

    def _idle_drift(self, timestamp: float, state: EyeVisualState) -> tuple[int, int]:
        if state not in {EyeVisualState.IDLE, EyeVisualState.LISTENING, EyeVisualState.SPEAKING}:
            return (0, 0)
        x = int(3 * math.sin(timestamp * 0.9))
        y = int(2 * math.sin(timestamp * 0.7 + 1.2))
        return x, y
