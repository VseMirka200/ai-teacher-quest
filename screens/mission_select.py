"""
Экран выбора миссий.
"""
from __future__ import annotations

import pygame

from core.settings import COLORS
from data.missions import MISSIONS
from screens.base import BaseScreen
from ui.components import Button, MissionCard


class MissionSelectScreen(BaseScreen):
    """Список миссий с описанием и статусом."""

    def _init_layout(self) -> None:
        fonts = self.context.fonts
        self.back_button = Button(
            pygame.Rect(40, 36, 200, 52),
            "В меню",
            fonts,
            on_click=self.manager.go_back,
        )
        self.cards: list[MissionCard] = []
        self._create_cards()
        self._recalculate_layout()

    def _create_cards(self) -> None:
        fonts = self.context.fonts
        def select_mission(mission_id: str) -> None:
            self.manager.change("mission", mission_id=mission_id)

        idx = 0
        for mission in MISSIONS:
            rect = pygame.Rect(0, 0, 360, 200)
            self.cards.append(MissionCard(rect, fonts, mission.__dict__, select_mission))
            idx += 1

    def _recalculate_layout(self) -> None:
        width, height = self.context.surface.get_size()
        padding_x = max(80, width // 20)
        padding_y = max(160, int(height * 0.18))
        columns = 2
        gap_x = max(48, width // 40)
        gap_y = max(200, int(height * 0.23))
        max_card_width = 420
        min_card_width = 320
        available_width = width - padding_x * 2 - gap_x * (columns - 1)
        card_width = max(min_card_width, min(max_card_width, available_width // columns))
        card_height = max(190, min(230, int(height * 0.22)))
        grid_width = columns * card_width + (columns - 1) * gap_x
        left_x = max(padding_x, (width - grid_width) // 2)

        for idx, card in enumerate(self.cards):
            col = idx % columns
            row = idx // columns
            x = left_x + col * (card_width + gap_x)
            y = padding_y + row * gap_y
            card.rect.update(x, y, card_width, card_height)

        self.title_pos = (width // 2, max(100, padding_y - 90))
        self.hint_pos = (width // 2, self.title_pos[1] + 40)
        self.grid_bottom = padding_y + (len(self.cards) // columns + (len(self.cards) % columns > 0) - 1) * gap_y + card_height

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        for card in self.cards:
            card.handle_event(event)

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        for card in self.cards:
            card.update(dt, mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        fonts = self.context.fonts
        title = fonts.render("Выберите миссию", 56, COLORS.text_primary, bold=True)
        surface.blit(title, title.get_rect(center=self.title_pos))

        hint = fonts.render(
            "Каждая миссия — новая учебная ситуация. Заработайте 3 звезды!",
            26,
            COLORS.text_secondary,
        )
        surface.blit(hint, hint.get_rect(center=self.hint_pos))

        for mission, card in zip(MISSIONS, self.cards):
            progress = self.context.progress.missions.get(mission.id)
            card.draw(surface, progress.__dict__ if progress else None)

    def on_resize(self, size: tuple[int, int]) -> None:
        self._recalculate_layout()

