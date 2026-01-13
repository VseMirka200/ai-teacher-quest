"""
Менеджер шрифтов для игры.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

import pygame

PREFERRED_FONTS = ["Segoe UI", "Verdana", "Calibri", "Arial"]


@dataclass
class FontManager:
    """Загружает и кэширует шрифты разных размеров."""

    base_name: str = ""
    _cache: Dict[Tuple[int, bool], pygame.font.Font] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        pygame.font.init()
        self.base_name = self._find_available_font()

    @staticmethod
    def _find_available_font() -> str:
        for name in PREFERRED_FONTS:
            path = pygame.font.match_font(name)
            if path:
                return path
        return pygame.font.get_default_font()

    def get(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self._cache:
            font = pygame.font.Font(self.base_name, size)
            font.set_bold(bold)
            self._cache[key] = font
        return self._cache[key]

    def render(self, text: str, size: int, color, bold: bool = False) -> pygame.Surface:
        font = self.get(size, bold=bold)
        return font.render(text, True, color)

