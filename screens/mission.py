"""
Экран прохождения миссии.
"""
from __future__ import annotations

import textwrap
from typing import List, Optional

import pygame

from ai.engine import AIEngine, EvaluationResult
from core.settings import COLORS, CRITERIA_META, GameTexts, MAX_PROMPT_LENGTH, MAX_PROMPT_HISTORY
from data.missions import Mission, get_mission
from screens.base import BaseScreen
from ui.components import Button, StarMeter, TextInput, Tooltip, TooltipManager, draw_rounded_rect, draw_shadow


class MissionScreen(BaseScreen):
    """Основной интерактив с вводом промптов."""

    def __init__(self, manager, context, mission_id: str) -> None:
        self.mission: Mission = get_mission(mission_id)
        self.ai_engine: AIEngine = context.ai_engine
        self.evaluation: Optional[EvaluationResult] = None
        self.status_message = ""
        self.status_color = COLORS.text_secondary
        self.tooltip_manager = TooltipManager(context.fonts)
        super().__init__(manager, context)

    def _init_layout(self) -> None:
        fonts = self.context.fonts
        self.back_button = Button(
            pygame.Rect(40, 36, 220, 52),
            "К миссиям",
            fonts,
            on_click=self.manager.go_back,
        )
        self.scenario_rect = pygame.Rect(0, 0, 10, 10)
        self.prompt_input = TextInput(
            pygame.Rect(0, 0, 10, 10),
            fonts,
            placeholder="Сформулируйте промпт для ИИ...",
            max_length=MAX_PROMPT_LENGTH,
        )
        self.retry_button = Button(
            pygame.Rect(0, 0, 10, 10),
            "Попробовать снова",
            fonts,
            on_click=self._reset_prompt,
        )
        self.send_button = Button(
            pygame.Rect(0, 0, 10, 10),
            "Отправить промпт",
            fonts,
            on_click=self._submit_prompt,
            accent=True,
        )
        self.finish_button = Button(
            pygame.Rect(0, 0, 10, 10),
            "Завершить",
            fonts,
            on_click=self._complete_mission,
        )
        self.ai_panel_rect = pygame.Rect(0, 0, 10, 10)
        self.answer_wrap_width = 36
        self.total_star_meter = StarMeter(pygame.Rect(0, 0, 10, 10), fonts)
        self.criteria_side = False
        self.eval_column_x = 0
        self.eval_column_top = 0
        self.eval_column_width = 0
        self.criteria_rects: List[pygame.Rect] = []
        self.status_position = (60, 620)
        self.history: List[EvaluationResult] = []
        self.history_index: int = -1
        self.history_button_rects: List[pygame.Rect] = []
        self.history_nav_y = 0
        self._recalculate_layout()
        self.ai_response_lines: List[str] = []

    def _recalculate_layout(self) -> None:
        width, height = self.context.surface.get_size()
        padding = max(48, width // 24)
        gutter = max(40, width // 40)
        max_content_width = min(max(900, width - padding * 2), 1180)
        right_width = max(520, int(max_content_width * 0.34))
        left_width = max(560, max_content_width - right_width - gutter)
        container_width = left_width + gutter + right_width
        start_x = max(padding, (width - container_width) // 2)
        scenario_top = max(120, int(height * 0.1))
        scenario_height = min(320, max(260, int(height * 0.3)))
        prompt_height = min(220, max(180, int(height * 0.22)))
        button_spacing = 18

        self.scenario_rect.update(start_x, scenario_top, left_width, scenario_height)
        prompt_rect = pygame.Rect(start_x, self.scenario_rect.bottom + 30, left_width, prompt_height)
        self.prompt_input.rect = prompt_rect

        buttons_top = self.prompt_input.rect.bottom + 20
        self.retry_button.rect = pygame.Rect(start_x, buttons_top, left_width, 54)
        self.send_button.rect = pygame.Rect(start_x, buttons_top + 54 + button_spacing, left_width, 60)
        self.finish_button.rect = pygame.Rect(
            start_x, buttons_top + 2 * (54 + button_spacing), left_width, 54
        )

        right_x = start_x + left_width + gutter
        ai_height = max(scenario_height + prompt_height - 20, 360)
        self.ai_panel_rect.update(right_x, scenario_top, right_width, ai_height)
        self.answer_wrap_width = max(36, self.ai_panel_rect.width // 12)

        side_space = width - (right_x + right_width) - padding
        if side_space >= 260:
            self.criteria_side = True
            self.eval_column_width = min(320, side_space)
            self.eval_column_x = width - padding - self.eval_column_width
            self.eval_column_top = scenario_top
            self.total_star_meter.rect = pygame.Rect(
                self.eval_column_x,
                self.eval_column_top,
                self.eval_column_width,
                40,
            )
        else:
            self.criteria_side = False
            self.eval_column_width = self.ai_panel_rect.width
            self.eval_column_x = self.ai_panel_rect.x
            self.eval_column_top = self.ai_panel_rect.bottom + 16
            self.total_star_meter.rect = pygame.Rect(
                self.eval_column_x,
                self.eval_column_top,
                self.ai_panel_rect.width,
                40,
            )
            self.eval_column_top = self.total_star_meter.rect.bottom + 30
        self.status_position = (start_x, self.finish_button.rect.bottom + 16)
        self.history_nav_y = self.ai_panel_rect.bottom + 24
        self._refresh_current_answer_lines()

        self._build_tooltips()

    def on_resize(self, size: tuple[int, int]) -> None:
        self._recalculate_layout()

    def _build_tooltips(self) -> None:
        height = self.context.surface.get_height()
        if self.criteria_side:
            start_x = self.eval_column_x
            y = self.total_star_meter.rect.bottom + 24
            width = self.eval_column_width
        else:
            start_x = self.eval_column_x
            y = self.eval_column_top
            width = self.eval_column_width
        self.criteria_rects = []
        max_height = height
        for cid in CRITERIA_META:
            if self.criteria_side:
                rect_height = 120
            else:
                rect_height = 100
            rect = pygame.Rect(start_x, y, width, rect_height)
            self.criteria_rects.append(rect)
            y += rect_height + 12
        self.tooltips = [
            Tooltip(CRITERIA_META[cid]["tooltip"], rect) for cid, rect in zip(CRITERIA_META, self.criteria_rects)
        ]

    def _submit_prompt(self) -> None:
        text = self.prompt_input.text.strip()
        if not text:
            self.status_message = GameTexts.EMPTY_PROMPT_WARNING
            self.status_color = COLORS.warning
            return
        if len(text) > MAX_PROMPT_LENGTH:
            self.status_message = GameTexts.PROMPT_LIMIT_WARNING
            self.status_color = COLORS.warning
            return

        evaluation = self.ai_engine.evaluate_prompt(text, self.mission)
        self._append_history(evaluation)
        self.status_message = "Промпт оценён!"
        self.status_color = COLORS.accent_secondary

    def _reset_prompt(self) -> None:
        self.prompt_input.clear()
        self.status_message = GameTexts.RETRY_HINT
        self.status_color = COLORS.text_secondary

    def _complete_mission(self) -> None:
        if not self.evaluation:
            self.status_message = "Сначала отправьте промпт."
            self.status_color = COLORS.warning
            return
        if self.evaluation.total_score < self.mission.success_threshold:
            self.status_message = GameTexts.NOT_READY_YET
            self.status_color = COLORS.warning
            return
        self.context.progress.update_mission(
            self.mission.id, self.evaluation.total_score, self.evaluation.total_stars
        )
        result_payload = {
            "mission": self.mission,
            "score": self.evaluation.total_score,
            "stars": self.evaluation.total_stars,
            "feedback": {c: s.feedback for c, s in self.evaluation.scores.items()},
            "issues": self.evaluation.issues,
        }
        self.manager.change("results", result=result_payload)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        submitted = self.prompt_input.handle_event(event)
        if submitted:
            self._submit_prompt()
        self.send_button.handle_event(event)
        self.retry_button.handle_event(event)
        self.finish_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in enumerate(self.history_button_rects):
                if rect.collidepoint(event.pos):
                    self._select_history(idx)
                    break

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        self.prompt_input.update(dt)
        self.send_button.update(dt, mouse_pos)
        self.retry_button.update(dt, mouse_pos)
        self.finish_button.update(dt, mouse_pos)
        self.tooltip_manager.update(mouse_pos, self.tooltips)

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        fonts = self.context.fonts
        self._draw_scenario(surface, fonts)
        self._draw_ai_response(surface, fonts)
        self.prompt_input.draw(surface)
        self.send_button.draw(surface)
        self.retry_button.draw(surface)
        self.finish_button.draw(surface)
        self._draw_criteria(surface, fonts)
        self.total_star_meter.draw(surface)
        if self.status_message:
            status = fonts.render(self.status_message, 22, self.status_color)
            surface.blit(status, self.status_position)
        self.tooltip_manager.draw(surface)

    def _draw_scenario(self, surface: pygame.Surface, fonts) -> None:
        card = self.scenario_rect
        draw_shadow(surface, card, blur=5, alpha=70)
        draw_rounded_rect(surface, COLORS.surface, card, radius=20)
        title = fonts.render(self.mission.title, 32, COLORS.text_primary, bold=True)
        width_chars = max(42, self.scenario_rect.width // 14)
        scenario_lines = self._wrap_text(self.mission.scenario, width_chars)
        surface.blit(title, (card.x + 20, card.y + 20))
        y = card.y + 70
        for line in scenario_lines:
            label = fonts.render(line, 22, COLORS.text_secondary)
            surface.blit(label, (card.x + 20, y))
            y += label.get_height() + 6

    def _draw_ai_response(self, surface: pygame.Surface, fonts) -> None:
        panel = self.ai_panel_rect
        draw_shadow(surface, panel, blur=5, alpha=70)
        draw_rounded_rect(surface, COLORS.surface_variant, panel, radius=18)
        title = fonts.render("Ответ ИИ", 28, COLORS.text_primary, bold=True)
        surface.blit(title, (panel.x + 20, panel.y + 12))

        if self.ai_response_lines:
            y = panel.y + 60
            for line in self.ai_response_lines:
                label = fonts.render(line, 20, COLORS.text_secondary)
                surface.blit(label, (panel.x + 20, y))
                y += label.get_height() + 4
        else:
            placeholder = fonts.render("Сформулируйте промпт, чтобы увидеть ответ.", 20, COLORS.text_secondary)
            surface.blit(placeholder, (panel.x + 20, panel.y + 80))
        self._draw_history_nav(surface)

    def _draw_criteria(self, surface: pygame.Surface, fonts) -> None:
        for (cid, meta), rect in zip(CRITERIA_META.items(), self.criteria_rects):
            draw_shadow(surface, rect, blur=3, alpha=40)
            draw_rounded_rect(surface, COLORS.surface, rect, radius=14)
            title = fonts.render(meta["title"], 22, COLORS.text_primary)
            surface.blit(title, (rect.x + 12, rect.y + 12))
            score_text = "-"
            if self.evaluation:
                score = self.evaluation.scores[cid]
                score_text = f"{score.stars}/3"
                wrap_width = max(24, rect.width // 14)
                feedback_lines = self._wrap_text(score.feedback, wrap_width)
                feedback_y = rect.y + 40
                for line in feedback_lines:
                    feedback = fonts.render(line, 16, COLORS.text_secondary)
                    surface.blit(feedback, (rect.x + 12, feedback_y))
                    feedback_y += feedback.get_height() + 2
            value = fonts.render(score_text, 20, COLORS.accent_secondary)
            surface.blit(value, (rect.right - 70, rect.y + 12))

    def _wrap_text(self, text: str, width: int) -> List[str]:
        return textwrap.wrap(text, width)

    def _append_history(self, evaluation: EvaluationResult) -> None:
        self.history.append(evaluation)
        if len(self.history) > MAX_PROMPT_HISTORY:
            self.history.pop(0)
            self.history_index = max(-1, self.history_index - 1)
        self._select_history(len(self.history) - 1)

    def _select_history(self, index: int) -> None:
        if not self.history:
            return
        index = max(0, min(index, len(self.history) - 1))
        self.history_index = index
        self.evaluation = self.history[index]
        self.total_star_meter.set_value(self.evaluation.total_stars)
        self._refresh_current_answer_lines()

    def _refresh_current_answer_lines(self) -> None:
        if 0 <= self.history_index < len(self.history):
            answer = self.history[self.history_index].ai_answer
            self.ai_response_lines = self._wrap_text(answer, self.answer_wrap_width)
        elif self.evaluation:
            self.ai_response_lines = self._wrap_text(self.evaluation.ai_answer, self.answer_wrap_width)

    def _draw_history_nav(self, surface: pygame.Surface) -> None:
        if len(self.history) <= 1:
            self.history_button_rects = []
            return
        total_width = len(self.history) * 28 + (len(self.history) - 1) * 8
        start_x = self.ai_panel_rect.centerx - total_width // 2
        self.history_button_rects = []
        for idx in range(len(self.history)):
            rect = pygame.Rect(0, 0, 20, 20)
            rect.center = (start_x + idx * 28, self.history_nav_y)
            self.history_button_rects.append(rect)
            color = COLORS.accent_secondary if idx == self.history_index else COLORS.surface_variant
            pygame.draw.circle(surface, color, rect.center, rect.width // 2)
        caption = self.context.fonts.render("История ответов", 16, COLORS.text_secondary)
        surface.blit(caption, caption.get_rect(center=(self.ai_panel_rect.centerx, self.history_nav_y - 18)))

