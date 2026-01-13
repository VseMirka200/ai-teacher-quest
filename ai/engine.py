"""
Простая логика симуляции ИИ и оценивания промптов.
"""
from __future__ import annotations

import random
import textwrap
from dataclasses import dataclass
from typing import Dict, List

from core.settings import CRITERIA_META, MAX_PROMPT_LENGTH

ACTION_KEYWORDS = [
    "объясни",
    "расскажи",
    "составь",
    "создай",
    "подготовь",
    "переведи",
    "проанализируй",
]

CONSTRAINT_KEYWORDS = [
    "в формате",
    "в виде",
    "не более",
    "пункта",
    "пунктов",
    "шагов",
    "примеров",
]

ETHICS_KEYWORDS = [
    "честност",
    "без плагиата",
    "не списывая",
    "самостоятельно",
    "не выдавай ответов",
]

AUDIENCE_KEYWORDS = [
    "класс",
    "курс",
    "студент",
    "ученик",
    "нович",
    "начинающ",
    "продвинут",
]


@dataclass
class CriterionScore:
    criterion_id: str
    stars: int
    feedback: str


@dataclass
class EvaluationResult:
    prompt: str
    total_score: int
    total_stars: int
    scores: Dict[str, CriterionScore]
    ai_answer: str
    issues: List[str]


class AIEngine:
    """Правила анализа промптов и генерации ответов."""

    def __init__(self) -> None:
        self.random = random.Random()

    def evaluate_prompt(self, prompt: str, mission: "Mission") -> EvaluationResult:  # noqa: F821
        text = prompt.strip()
        normalized = text.lower()

        scores: Dict[str, CriterionScore] = {}
        issues: List[str] = []

        clarity = self._score_clarity(normalized)
        scores["clarity"] = CriterionScore("clarity", clarity, self._clarity_feedback(clarity))

        context = self._score_context(normalized, mission)
        scores["context"] = CriterionScore("context", context, self._context_feedback(context))

        constraints = self._score_constraints(normalized)
        scores["constraints"] = CriterionScore("constraints", constraints, self._constraint_feedback(constraints))

        ethics = self._score_ethics(normalized, mission)
        scores["ethics"] = CriterionScore("ethics", ethics, self._ethic_feedback(ethics))

        total_score = sum(score.stars for score in scores.values())
        total_stars = min(3, round(total_score / len(scores)))

        if total_stars < 2:
            issues.append("Ответ ИИ может содержать неточности — перепроверьте факты.")
        if len(text) < 40:
            issues.append("Промпт слишком короткий, добавьте деталей.")
        if len(text) > MAX_PROMPT_LENGTH * 0.9:
            issues.append("Промпт близок к лимиту, подумайте о сокращении.")

        ai_answer = self._generate_answer(text, mission, total_stars)

        return EvaluationResult(
            prompt=text,
            total_score=total_score,
            total_stars=total_stars,
            scores=scores,
            ai_answer=ai_answer,
            issues=issues,
        )

    def _score_clarity(self, normalized: str) -> int:
        has_action = any(keyword in normalized for keyword in ACTION_KEYWORDS)
        return 3 if has_action and len(normalized) > 40 else (2 if has_action else 1)

    def _score_context(self, normalized: str, mission: "Mission") -> int:  # noqa: F821
        has_context = any(keyword in normalized for keyword in AUDIENCE_KEYWORDS)
        mission_hint = any(token in normalized for token in mission.context_keywords)
        if has_context and mission_hint:
            return 3
        if has_context or mission_hint:
            return 2
        return 1

    def _score_constraints(self, normalized: str) -> int:
        has_constraints = any(keyword in normalized for keyword in CONSTRAINT_KEYWORDS)
        has_numbers = any(char.isdigit() for char in normalized)
        if has_constraints and has_numbers:
            return 3
        if has_constraints or has_numbers:
            return 2
        return 1

    def _score_ethics(self, normalized: str, mission: "Mission") -> int:  # noqa: F821
        mentions_ethics = any(keyword in normalized for keyword in ETHICS_KEYWORDS)
        mentions_honesty = "честн" in normalized or "этич" in normalized
        if mission.requires_ethics and (mentions_ethics or mentions_honesty):
            return 3
        if mission.requires_ethics:
            return 1
        return 2 if mentions_ethics else 1

    @staticmethod
    def _clarity_feedback(stars: int) -> str:
        if stars == 3:
            return "Цель изложена чётко, ИИ понимает ожидаемый результат."
        if stars == 2:
            return "Добавьте конкретику: что именно должен сделать ИИ."
        return "Опишите задачу подробнее: глаголы действия и результат."

    @staticmethod
    def _context_feedback(stars: int) -> str:
        if stars == 3:
            return "Контекст аудитории указан."
        if stars == 2:
            return "Уточните уровень или возраст обучающихся."
        return "ИИ не знает, для кого ответ — добавьте описание аудитории."

    @staticmethod
    def _constraint_feedback(stars: int) -> str:
        if stars == 3:
            return "Формат запроса и ограничения понятны."
        if stars == 2:
            return "Пропишите желаемый формат, количество пунктов или стиль."
        return "Нет ограничений — ИИ выдаст общий ответ."

    @staticmethod
    def _ethic_feedback(stars: int) -> str:
        if stars == 3:
            return "Подчёркнута академическая честность или безопасность."
        if stars == 2:
            return "Подумайте о рисках и этичных ограничениях."
        return "Добавьте упоминание академической честности."

    def _generate_answer(self, prompt: str, mission: "Mission", stars: int) -> str:  # noqa: F821
        base_response = textwrap.dedent(
            f"""
            Принято! Вот предложение для ситуации «{mission.title}»:

            1. {mission.response_templates[0]}
            2. {mission.response_templates[1]}
            3. {mission.response_templates[2]}
            """
        ).strip()

        if stars >= 2:
            return base_response

        hallucination = self.random.choice(
            [
                "⚠ Возможна неточность: в ответе встречается лишний термин, перепроверьте его.",
                "⚠ Ответ получился общим — попробуйте задать формат.",
            ]
        )
        return f"{base_response}\n\n{hallucination}"

