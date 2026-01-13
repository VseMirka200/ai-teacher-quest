"""
Глобальные настройки игры AI Teacher Quest.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class WindowConfig:
    """Параметры окна, вынесенные в отдельную структуру."""

    width: int = 1500
    height: int = 900
    fps: int = 60
    title: str = "AI Teacher Quest"
    fullscreen: bool = False


@dataclass(frozen=True)
class Palette:
    """Набор базовых цветов интерфейса."""

    background_top: Tuple[int, int, int] = (30, 33, 77)
    background_bottom: Tuple[int, int, int] = (15, 18, 45)
    accent: Tuple[int, int, int] = (120, 110, 255)
    accent_soft: Tuple[int, int, int] = (173, 159, 255)
    accent_secondary: Tuple[int, int, int] = (74, 222, 205)
    surface: Tuple[int, int, int] = (38, 43, 86)
    surface_variant: Tuple[int, int, int] = (52, 57, 107)
    text_primary: Tuple[int, int, int] = (239, 240, 250)
    text_secondary: Tuple[int, int, int] = (192, 197, 232)
    warning: Tuple[int, int, int] = (255, 99, 146)
    success: Tuple[int, int, int] = (104, 227, 168)


WINDOW = WindowConfig()
COLORS = Palette()

MAX_PROMPT_LENGTH = 600
MIN_PROMPT_LENGTH = 12
MAX_PROMPT_HISTORY = 3

# Метаданные критериев оценки промптов. Используются UI и движком.
CRITERIA_META: Dict[str, Dict[str, str]] = {
    "clarity": {
        "title": "Ясность задачи",
        "tooltip": "Сформулируйте чётко цель: что именно должен сделать ИИ.",
    },
    "context": {
        "title": "Контекст аудитории",
        "tooltip": "Опишите, кто получит ответ: возраст, уровень знаний.",
    },
    "constraints": {
        "title": "Формат и ограничения",
        "tooltip": "Добавьте формат, количество пунктов или стиль ответа.",
    },
    "ethics": {
        "title": "Этичность",
        "tooltip": "Напомните об академической честности и корректности.",
    },
}


class GameTexts:
    """Статические строки, собранные в одном месте для удобства перевода."""

    EMPTY_PROMPT_WARNING = "Введите текст промпта"
    PROMPT_LIMIT_WARNING = (
        f"Промпт ограничен {MAX_PROMPT_LENGTH} символами."
    )
    RETRY_HINT = "Попробуйте уточнить задачу и добавить контекст."
    READY_TO_FINISH = "Можно завершить миссию!"
    NOT_READY_YET = "Повысите качество промпта, чтобы завершить миссию."

