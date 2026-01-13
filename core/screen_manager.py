"""
Менеджер экранов/сцен игры.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

import pygame

from core.background import DynamicBackground
from core.context import GameContext

if False:  # pragma: no cover - подсказка для типов
    from screens.base import BaseScreen


ScreenFactory = Callable[[GameContext], "BaseScreen"]


class ScreenManager:
    """Отвечает за переключение экранов, переходы и фон."""

    def __init__(self, context: GameContext) -> None:
        self.context = context
        self._factories: Dict[str, Callable[[GameContext, dict], "BaseScreen"]] = {}
        self._current: Optional["BaseScreen"] = None
        self._current_name: str = ""
        self._history: list[str] = []

        self._transition_active = False
        self._transition_alpha = 0.0
        self._transition_direction = 1  # 1 — затемнение, -1 — появление
        self._pending_target: Optional[str] = None
        self._pending_kwargs: dict = {}

        self._fade_surface = pygame.Surface(self.context.surface.get_size(), pygame.SRCALPHA)
        self.background = DynamicBackground(self.context.surface.get_size())

        self._register_defaults()
        self.change("menu")

    def _register_defaults(self) -> None:
        from screens.menu import MenuScreen
        from screens.mission import MissionScreen
        from screens.mission_select import MissionSelectScreen
        from screens.results import ResultsScreen
        from screens.settings import SettingsScreen
        from screens.tutorial import TutorialScreen

        self._factories = {
            "menu": lambda ctx, kwargs=None: MenuScreen(self, ctx),
            "tutorial": lambda ctx, kwargs=None: TutorialScreen(self, ctx),
            "mission_select": lambda ctx, kwargs=None: MissionSelectScreen(self, ctx),
            "mission": lambda ctx, kwargs=None: MissionScreen(self, ctx, **(kwargs or {})),
            "results": lambda ctx, kwargs=None: ResultsScreen(self, ctx, **(kwargs or {})),
            "settings": lambda ctx, kwargs=None: SettingsScreen(self, ctx),
        }

    def change(self, screen_name: str, *, remember: bool = True, **kwargs) -> None:
        if screen_name not in self._factories:
            raise ValueError(f"Экран {screen_name} не зарегистрирован")
        if self._transition_active:
            return
        if remember and self._current_name:
            self._history.append(self._current_name)
        self._pending_target = screen_name
        self._pending_kwargs = kwargs
        self._transition_active = True
        self._transition_direction = 1
        self._transition_alpha = 0.0

    def go_back(self) -> None:
        if not self._history:
            return
        target = self._history.pop()
        self.change(target, remember=False)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._current and not self._transition_active:
            self._current.handle_event(event)

    def update(self, dt: float) -> None:
        self.background.update(dt)
        if self._current:
            self._current.update(dt)
        if self._transition_active:
            speed = 2.0
            self._transition_alpha += dt * speed * self._transition_direction
            if self._transition_direction == 1 and self._transition_alpha >= 1:
                self._activate_pending()
                self._transition_direction = -1
                self._transition_alpha = 1
            elif self._transition_direction == -1 and self._transition_alpha <= 0:
                self._transition_active = False
                self._transition_alpha = 0

    def draw(self) -> None:
        surface = self.context.surface
        self.background.draw(surface)
        if self._current:
            self._current.draw(surface)
        if self._transition_active:
            self._fade_surface.fill((10, 12, 25, int(255 * self._transition_alpha)))
            surface.blit(self._fade_surface, (0, 0))

    def handle_resize(self, size: tuple[int, int]) -> None:
        self._fade_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.background.resize(size)
        if self._current and hasattr(self._current, "on_resize"):
            self._current.on_resize(size)

    def _activate_pending(self) -> None:
        if not self._pending_target:
            return
        factory = self._factories[self._pending_target]
        self._current = factory(self.context, self._pending_kwargs)
        self._current_name = self._pending_target
        self._pending_target = None
        self._pending_kwargs = {}

