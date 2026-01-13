"""
Экран результатов миссии.
"""
from __future__ import annotations

import pygame

from core.settings import COLORS
from screens.base import BaseScreen
from ui.components import Button, StarMeter, draw_rounded_rect, draw_shadow


class ResultsScreen(BaseScreen):
    """Показывает итог миссии и рекомендации."""

    def __init__(self, manager, context, result: dict) -> None:
        self.result = result
        super().__init__(manager, context)

    def _init_layout(self) -> None:
        fonts = self.context.fonts
        self.back_button = Button(
            pygame.Rect(32, 32, 200, 48),
            "К миссиям",
            fonts,
            on_click=lambda: self.manager.change("mission_select", remember=False),
        )
        self.retry_button = Button(
            pygame.Rect(400, 520, 220, 54),
            "Переиграть миссию",
            fonts,
            on_click=lambda: self.manager.change("mission", mission_id=self.result["mission"].id),
            accent=True,
        )
        self.select_button = Button(
            pygame.Rect(640, 520, 220, 54),
            "Выбор миссий",
            fonts,
            on_click=lambda: self.manager.change("mission_select", remember=False),
        )
        self.star_meter = StarMeter(pygame.Rect(500, 360, 200, 40), fonts)
        self.star_meter.set_value(self.result["stars"])

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        self.retry_button.handle_event(event)
        self.select_button.handle_event(event)

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        self.retry_button.update(dt, mouse_pos)
        self.select_button.update(dt, mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        fonts = self.context.fonts
        panel = pygame.Rect(200, 120, 840, 360)
        draw_shadow(surface, panel, blur=8, alpha=90)
        draw_rounded_rect(surface, COLORS.surface, panel, radius=24)

        mission = self.result["mission"]
        title = fonts.render(f"Миссия: {mission.title}", 36, COLORS.text_primary, bold=True)
        surface.blit(title, (panel.x + 20, panel.y + 20))

        score_text = fonts.render(f"Баллы: {self.result['score']}", 28, COLORS.accent_secondary)
        surface.blit(score_text, (panel.x + 20, panel.y + 80))

        self.star_meter.draw(surface)

        feedback_y = panel.y + 140
        for cid, text in self.result["feedback"].items():
            line = fonts.render(text, 20, COLORS.text_secondary)
            surface.blit(line, (panel.x + 20, feedback_y))
            feedback_y += line.get_height() + 6

        if self.result["issues"]:
            issues_title = fonts.render("Обратите внимание:", 22, COLORS.warning)
            surface.blit(issues_title, (panel.x + 20, feedback_y + 10))
            y = feedback_y + 50
            for issue in self.result["issues"]:
                issue_label = fonts.render(f"- {issue}", 20, COLORS.text_secondary)
                surface.blit(issue_label, (panel.x + 40, y))
                y += issue_label.get_height() + 4

        self.retry_button.draw(surface)
        self.select_button.draw(surface)

