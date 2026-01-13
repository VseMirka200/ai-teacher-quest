"""
Набор переиспользуемых UI-компонентов.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import pygame

from core.settings import COLORS
from ui.animations import clamp, lerp


def draw_rounded_rect(surface: pygame.Surface, color, rect: pygame.Rect, radius: int = 12) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_shadow(surface: pygame.Surface, rect: pygame.Rect, blur: int = 4, alpha: int = 80) -> None:
    shadow_rect = rect.inflate(blur * 2, blur * 2).move(0, 4)
    shadow = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow, (*COLORS.background_bottom, alpha), shadow.get_rect(), border_radius=rect.height // 4)
    surface.blit(shadow, shadow_rect.topleft)


class Button:
    """Стандартная кнопка с плавной анимацией наведения."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        fonts,
        *,
        on_click: Optional[Callable[[], None]] = None,
        accent: bool = False,
    ) -> None:
        self.rect = rect
        self.text = text
        self.fonts = fonts
        self.on_click = on_click
        self.accent = accent

        self._hover_progress = 0.0
        self._pressed = False
        self._enabled = True

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self._enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
            self._pressed = False

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        hovered = self.rect.collidepoint(mouse_pos) and self._enabled
        target = 1.0 if hovered else 0.0
        self._hover_progress = lerp(self._hover_progress, target, min(dt * 8, 1))

    def draw(self, surface: pygame.Surface) -> None:
        draw_shadow(surface, self.rect, blur=3, alpha=50)
        base_color = COLORS.accent if self.accent else COLORS.surface
        hover_color = COLORS.accent_secondary if self.accent else COLORS.surface_variant
        color = [
            int(base_color[i] * (1 - self._hover_progress) + hover_color[i] * self._hover_progress)
            for i in range(3)
        ]
        draw_rounded_rect(surface, color, self.rect, radius=16)

        label = self.fonts.render(self.text, 26, COLORS.text_primary, bold=self.accent)
        text_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, text_rect)


class ToggleButton(Button):
    """Кнопка-переключатель для экрана настроек."""

    def __init__(self, rect: pygame.Rect, text: str, fonts, *, initial: bool = True, on_toggle=None):
        super().__init__(rect, text, fonts, accent=False)
        self.state = initial
        self.on_toggle = on_toggle

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                if self.on_toggle:
                    self.on_toggle(self.state)

    def draw(self, surface: pygame.Surface) -> None:
        indicator_rect = pygame.Rect(self.rect.x + 12, self.rect.centery - 10, 48, 20)
        knob_rect = pygame.Rect(0, 0, 18, 18)
        knob_rect.centery = indicator_rect.centery
        knob_rect.left = indicator_rect.left + 2 if not self.state else indicator_rect.right - 20

        bar_color = COLORS.surface_variant if not self.state else COLORS.accent_secondary
        draw_rounded_rect(surface, COLORS.surface, self.rect, radius=14)
        draw_rounded_rect(surface, bar_color, indicator_rect, radius=12)
        draw_rounded_rect(surface, COLORS.surface, knob_rect, radius=9)

        label = self.fonts.render(self.text, 22, COLORS.text_primary)
        surface.blit(label, (self.rect.x + 72, self.rect.centery - label.get_height() // 2))


class TextInput:
    """Многострочное поле ввода для промптов."""

    def __init__(self, rect: pygame.Rect, fonts, *, placeholder: str = "", max_length: int = 600) -> None:
        self.rect = rect
        self.fonts = fonts
        self.placeholder = placeholder
        self.max_length = max_length

        self.text = ""
        self.active = False
        self._caret_visible = True
        self._caret_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> Optional[bool]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                if len(self.text) < self.max_length and (event.unicode.isprintable() or event.unicode == "\n"):
                    self.text += event.unicode
        return None

    def update(self, dt: float) -> None:
        if self.active:
            self._caret_timer += dt
            if self._caret_timer >= 0.5:
                self._caret_visible = not self._caret_visible
                self._caret_timer = 0

    def clear(self) -> None:
        self.text = ""

    def draw(self, surface: pygame.Surface) -> None:
        draw_shadow(surface, self.rect, blur=6)
        draw_rounded_rect(surface, COLORS.surface, self.rect, radius=12)

        text_color = COLORS.text_primary
        lines = self._wrap_text(self.text or self.placeholder, width=self.rect.width - 32)
        y = self.rect.y + 16
        for line in lines:
            color = COLORS.text_secondary if (not self.text and line == self.placeholder) else text_color
            label = self.fonts.render(line, 22, color)
            surface.blit(label, (self.rect.x + 16, y))
            y += label.get_height() + 6

        if self.active and self._caret_visible:
            caret_y = self.rect.y + 16 + (len(lines) - 1) * (self.fonts.get(22).get_height() + 6)
            caret_x = self.rect.x + 16 + self.fonts.get(22).size(lines[-1])[0]
            pygame.draw.line(surface, COLORS.accent_secondary, (caret_x, caret_y), (caret_x, caret_y + 24), 2)

    def _wrap_text(self, text: str, width: int) -> List[str]:
        words = text.replace("\n", " \n ").split(" ")
        lines: List[str] = []
        current = ""
        for word in words:
            if word == "\n":
                lines.append(current)
                current = ""
                continue
            test_line = f"{current} {word}".strip()
            if self.fonts.get(22).size(test_line)[0] <= width:
                current = test_line
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]


@dataclass
class Tooltip:
    """Модель всплывающей подсказки."""

    text: str
    rect: pygame.Rect


class TooltipManager:
    """Простейший менеджер подсказок по наведению."""

    def __init__(self, fonts) -> None:
        self.fonts = fonts
        self.active_tooltip: Optional[Tooltip] = None

    def update(self, mouse_pos: Tuple[int, int], tooltips: List[Tooltip]) -> None:
        self.active_tooltip = None
        for tip in tooltips:
            if tip.rect.collidepoint(mouse_pos):
                self.active_tooltip = tip
                break

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active_tooltip:
            return
        padding = 12
        label = self.fonts.render(self.active_tooltip.text, 20, COLORS.text_primary)
        tip_rect = label.get_rect()
        tip_rect.inflate_ip(padding * 2, padding * 2)
        tip_rect.topleft = (
            min(self.active_tooltip.rect.right + 12, surface.get_width() - tip_rect.width - 16),
            max(self.active_tooltip.rect.top - tip_rect.height, 16),
        )

        draw_shadow(surface, tip_rect, blur=3, alpha=60)
        draw_rounded_rect(surface, COLORS.surface_variant, tip_rect, radius=12)
        surface.blit(label, (tip_rect.x + padding, tip_rect.y + padding))


class StarMeter:
    """Отображение количества звёзд (0-3)."""

    def __init__(self, rect: pygame.Rect, fonts, *, capacity: int = 3) -> None:
        self.rect = rect
        self.fonts = fonts
        self.capacity = capacity
        self.value = 0

    def set_value(self, stars: int) -> None:
        self.value = clamp(stars, 0, self.capacity)

    def draw(self, surface: pygame.Surface) -> None:
        gap = 56
        total_span = gap * (self.capacity - 1)
        start_x = self.rect.centerx - total_span / 2
        cy = self.rect.centery
        for i in range(self.capacity):
            cx = int(start_x + i * gap)
            color = COLORS.accent_secondary if i < self.value else COLORS.surface_variant
            pygame.draw.circle(surface, color, (cx, cy), 18)
            star_label = self.fonts.render("★", 22, COLORS.text_primary if i < self.value else COLORS.text_secondary)
            surface.blit(star_label, star_label.get_rect(center=(cx, cy)))


class MissionCard:
    """Карточка миссии для экрана выбора."""

    def __init__(self, rect: pygame.Rect, fonts, data: dict, on_click: Callable[[str], None]):
        self.rect = rect
        self.fonts = fonts
        self.data = data
        self.on_click = on_click
        self.hover = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click(self.data["id"])

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if hovered else 0.0
        self.hover = lerp(self.hover, target, min(dt * 6, 1))

    def draw(self, surface: pygame.Surface, progress: Optional[dict] = None) -> None:
        draw_shadow(surface, self.rect, blur=4, alpha=50)
        bg_color = [
            int(COLORS.surface[i] * (1 - self.hover) + COLORS.surface_variant[i] * self.hover)
            for i in range(3)
        ]
        draw_rounded_rect(surface, bg_color, self.rect, radius=18)

        title = self.fonts.render(self.data["title"], 26, COLORS.text_primary, bold=True)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 16))

        summary_font = self.fonts.get(20)
        summary_lines = self._wrap_text(summary_font, self.data["summary"], self.rect.width - 40)
        y = self.rect.y + 56
        for line in summary_lines:
            label = summary_font.render(line, True, COLORS.text_secondary)
            surface.blit(label, (self.rect.x + 20, y))
            y += label.get_height() + 4

        difficulty_label = self.fonts.render("Сложность:", 18, COLORS.text_secondary)
        difficulty_y = self.rect.bottom - 70
        surface.blit(difficulty_label, (self.rect.x + 20, difficulty_y))
        for i in range(3):
            cx = self.rect.x + 130 + i * 22
            cy = difficulty_y + 10
            color = COLORS.accent if i < self.data["difficulty"] else COLORS.surface_variant
            pygame.draw.circle(surface, color, (cx, cy), 8)

        status_text = "Не пройдено"
        if progress and progress.get("completed"):
            stars = progress.get("best_stars", 0)
            status_text = f"Пройдено: {stars}★"
        status_label = self.fonts.render(status_text, 18, COLORS.accent_secondary)
        surface.blit(status_label, (self.rect.x + 20, self.rect.bottom - 34))

    def _wrap_text(self, font: pygame.font.Font, text: str, max_width: int) -> List[str]:
        words = text.split()
        lines: List[str] = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

