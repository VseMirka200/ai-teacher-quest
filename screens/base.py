"""
Базовый экран, от которого наследуются остальные сцены.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame

from core.context import GameContext

if TYPE_CHECKING:
    from ui.components import Button


class BaseScreen:
    """Единый интерфейс для экранов."""

    def __init__(self, manager: "ScreenManager", context: GameContext) -> None:  # noqa: F821
        self.manager = manager
        self.context = context
        self.widgets = []
        self.back_button: Optional["Button"] = None  # noqa: F821
        self._init_layout()

    def _init_layout(self) -> None:
        """Вызывается в конце конструктора для настройки UI."""

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.back_button:
            self.back_button.handle_event(event)

    def update(self, dt: float) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if self.back_button:
            self.back_button.update(dt, mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        if self.back_button:
            self.back_button.draw(surface)

    def on_resize(self, size: tuple[int, int]) -> None:
        """Экран может переопределить реакцию на изменение размера."""

