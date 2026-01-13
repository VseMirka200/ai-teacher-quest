"""
Контекст игры: хранит объекты, доступные всем экранам.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

import pygame

from core.settings import WINDOW


@dataclass
class MissionProgress:
    """Информация о прохождении миссии."""

    best_score: int = 0
    best_stars: int = 0
    completed: bool = False


@dataclass
class GameProgress:
    """Глобальное состояние прохождения игры."""

    missions: Dict[str, MissionProgress] = field(default_factory=dict)
    last_result: Dict[str, int | str] = field(default_factory=dict)

    def update_mission(self, mission_id: str, score: int, stars: int) -> None:
        record = self.missions.setdefault(mission_id, MissionProgress())
        record.best_score = max(record.best_score, score)
        record.best_stars = max(record.best_stars, stars)
        record.completed = record.completed or stars > 0
        self.last_result = {"mission_id": mission_id, "score": score, "stars": stars}


@dataclass
class GameContext:
    """Общий контекст — поверхность окна, шрифты, ИИ-модуль, прогресс."""

    surface: pygame.Surface
    fonts: "FontManager"  # type: ignore  # определён в ui.fonts
    ai_engine: "AIEngine"  # type: ignore  # определён в ai.engine
    progress: GameProgress = field(default_factory=GameProgress)
    fullscreen: bool = False
    screen_size: Tuple[int, int] = field(default_factory=lambda: (WINDOW.width, WINDOW.height))
    _fullscreen_handler: Optional[Callable[[bool], pygame.Surface]] = field(default=None, repr=False)
    window = WINDOW

    def set_fullscreen_handler(self, handler: Callable[[bool], pygame.Surface]) -> None:
        self._fullscreen_handler = handler

    def apply_fullscreen(self, fullscreen: bool) -> None:
        if self._fullscreen_handler:
            self.surface = self._fullscreen_handler(fullscreen)
        self.fullscreen = fullscreen
        self.screen_size = self.surface.get_size()

    def toggle_fullscreen(self) -> None:
        self.apply_fullscreen(not self.fullscreen)

