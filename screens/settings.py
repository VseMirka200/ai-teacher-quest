"""
Экран настроек (минимальная функциональность).
"""
from __future__ import annotations

import pygame

from core.settings import COLORS
from screens.base import BaseScreen
from ui.components import Button, ToggleButton, draw_rounded_rect, draw_shadow


class SettingsScreen(BaseScreen):
    """Позволяет включать/выключать подсказки и анимации."""

    def _init_layout(self) -> None:
        fonts = self.context.fonts
        self.back_button = Button(
            pygame.Rect(32, 32, 180, 48),
            "Назад",
            fonts,
            on_click=self.manager.go_back,
        )
        start_y = 220
        spacing = 90
        width = 520
        self.fullscreen_toggle = ToggleButton(
            pygame.Rect(400, start_y, width, 60),
            "Полноэкранный режим (F11)",
            fonts,
            initial=self.context.fullscreen,
            on_toggle=self._handle_fullscreen_toggle,
        )
        self.toggles = [
            self.fullscreen_toggle,
            ToggleButton(
                pygame.Rect(400, start_y + spacing, width, 60),
                "Показывать подсказки",
                fonts,
                initial=True,
            ),
            ToggleButton(
                pygame.Rect(400, start_y + spacing * 2, width, 60),
                "Анимация кнопок",
                fonts,
                initial=True,
            ),
        ]

    def _handle_fullscreen_toggle(self, enabled: bool) -> None:
        self.context.apply_fullscreen(enabled)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        for toggle in self.toggles:
            toggle.handle_event(event)

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        for toggle in self.toggles:
            toggle.update(dt, mouse_pos)
        self.fullscreen_toggle.state = self.context.fullscreen

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        fonts = self.context.fonts
        panel = pygame.Rect(300, 140, 640, 400)
        draw_shadow(surface, panel, blur=6, alpha=80)
        draw_rounded_rect(surface, COLORS.surface, panel, radius=24)

        title = fonts.render("Настройки", 40, COLORS.text_primary, bold=True)
        surface.blit(title, (panel.x + 20, panel.y + 20))

        for toggle in self.toggles:
            toggle.draw(surface)

