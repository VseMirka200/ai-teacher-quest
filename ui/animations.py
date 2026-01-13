"""
Простые функции анимации и сглаживания.
"""
from __future__ import annotations


def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


def ease_in_out(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2

