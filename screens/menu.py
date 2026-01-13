"""
Главное меню игры.
"""
from __future__ import annotations

import math
import pygame

from core.settings import COLORS, WINDOW
from screens.base import BaseScreen
from ui.components import Button


class MenuScreen(BaseScreen):
    """Показывает заголовок и основные действия."""

    def _init_layout(self) -> None:
        fonts = self.context.fonts

        def start_game() -> None:
            self.manager.change("mission_select")

        def open_tutorial() -> None:
            self.manager.change("tutorial")

        def open_settings() -> None:
            self.manager.change("settings")

        def quit_game() -> None:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        button_rects = [
            pygame.Rect(0, 0, 320, 58) for _ in range(4)
        ]
        actions = [start_game, open_tutorial, open_settings, quit_game]
        labels = ["Новая игра", "Обучение", "Настройки", "Выход"]

        self.buttons = [
            Button(button_rects[i], labels[i], fonts, on_click=actions[i], accent=(i == 0))
            for i in range(4)
        ]
        self.title_animation = 0.0
        self.pulse = 0.0

        self.back_button = None
        self._recalculate_layout()

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(dt, mouse_pos)
        self.title_animation += dt
        self.pulse = 0.5 + 0.5 * math.sin(self.title_animation * 1.5)

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        fonts = self.context.fonts
        width, height = surface.get_size()

        title = fonts.render("AI Teacher Quest", 64, COLORS.text_primary, bold=True)
        subtitle = fonts.render(
            "Интерактивное обучение работе с промптами для преподавателей",
            28,
            COLORS.text_secondary,
        )
        title_rect = title.get_rect(center=(width // 2, int(height * 0.2) + int(self.pulse * 6)))
        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, title_rect.bottom + 40)))

        for btn in self.buttons:
            btn.draw(surface)

    def _recalculate_layout(self) -> None:
        width, height = self.context.surface.get_size()
        center_x = width // 2
        start_y = max(int(height * 0.45), 360)
        spacing = 72
        for idx, btn in enumerate(self.buttons):
            btn.rect.centerx = center_x
            btn.rect.y = start_y + idx * spacing

    def on_resize(self, size: tuple[int, int]) -> None:
        self._recalculate_layout()

