"""
Экран обучения.
"""
from __future__ import annotations

import textwrap

import pygame

from core.settings import COLORS, WINDOW
from data.tutorial import TUTORIAL_QUIZ, TUTORIAL_STEPS
from screens.base import BaseScreen
from ui.components import Button, draw_rounded_rect, draw_shadow


class TutorialScreen(BaseScreen):
    """Даёт краткое интерактивное объяснение промптов."""

    def _init_layout(self) -> None:
        fonts = self.context.fonts
        self.back_button = Button(
            pygame.Rect(40, 36, 180, 50),
            "Назад",
            fonts,
            on_click=self.manager.go_back,
        )

        padding = 80
        cards_gap = 60
        available_width = WINDOW.width - padding * 2 - cards_gap * (len(TUTORIAL_STEPS) - 1)
        card_width = available_width // len(TUTORIAL_STEPS)
        self.card_rects = [
            pygame.Rect(padding + idx * (card_width + cards_gap), 140, card_width, 240)
            for idx in range(len(TUTORIAL_STEPS))
        ]

        self.quiz_rect = pygame.Rect(padding, 430, WINDOW.width - padding * 2, 360)
        quiz_inner_x = self.quiz_rect.x + 40
        quiz_button_width = self.quiz_rect.width - 80
        quiz_y = self.quiz_rect.y + 140
        self.quiz_feedback = ""
        self.quiz_status_color = COLORS.text_secondary
        self.quiz_buttons = []

        for idx, option in enumerate(TUTORIAL_QUIZ["options"]):
            rect = pygame.Rect(quiz_inner_x, quiz_y + idx * 78, quiz_button_width, 60)
            btn = Button(rect, option["text"], fonts, on_click=lambda opt=option: self._check_option(opt))
            self.quiz_buttons.append(btn)

    def _check_option(self, option: dict) -> None:
        self.quiz_feedback = option["feedback"]
        self.quiz_status_color = COLORS.success if option["correct"] else COLORS.warning

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        for btn in self.quiz_buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.quiz_buttons:
            btn.update(dt, mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        fonts = self.context.fonts

        body_font = self.context.fonts.get(18)
        for idx, step in enumerate(TUTORIAL_STEPS):
            card_rect = self.card_rects[idx]
            draw_shadow(surface, card_rect, blur=4, alpha=60)
            draw_rounded_rect(surface, COLORS.surface, card_rect, radius=18)
            title = fonts.render(step["title"], 24, COLORS.text_primary, bold=True)
            surface.blit(title, (card_rect.x + 16, card_rect.y + 16))
            lines = textwrap.wrap(step["body"], width=max(32, card_rect.width // 11))
            y = card_rect.y + 60
            for line in lines:
                label = body_font.render(line, True, COLORS.text_secondary)
                surface.blit(label, (card_rect.x + 16, y))
                y += label.get_height() + 4

        quiz_rect = self.quiz_rect
        draw_shadow(surface, quiz_rect, blur=4, alpha=80)
        draw_rounded_rect(surface, COLORS.surface_variant, quiz_rect, radius=24)

        title = fonts.render("Мини-интерактив:", 32, COLORS.text_primary, bold=True)
        surface.blit(title, (quiz_rect.x + 24, quiz_rect.y + 24))

        scenario = fonts.render(TUTORIAL_QUIZ["scenario"], 24, COLORS.text_secondary)
        surface.blit(scenario, (quiz_rect.x + 24, quiz_rect.y + 70))

        for btn in self.quiz_buttons:
            btn.draw(surface)

        if self.quiz_feedback:
            feedback = fonts.render(self.quiz_feedback, 24, self.quiz_status_color)
            surface.blit(feedback, (quiz_rect.x + 24, quiz_rect.bottom - 52))

