"""
Анимированный фон: мягкий градиент и «узлы».
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import pygame

from core.settings import COLORS, WINDOW


@dataclass
class FloatingNode:
    """Простая частица для анимации."""

    position: pygame.math.Vector2
    velocity: pygame.math.Vector2
    radius: float
    base_radius: float
    color: Tuple[int, int, int]

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.radius = self.base_radius + (self.base_radius * 0.2) * math.sin(pygame.time.get_ticks() / 500.0)


class DynamicBackground:
    """Отвечает за отрисовку градиента и узлов."""

    def __init__(self, size: Tuple[int, int]) -> None:
        self.width, self.height = size
        self.gradient_surface = self._create_gradient_surface()
        self.nodes: List[FloatingNode] = self._spawn_nodes()

    def resize(self, size: Tuple[int, int]) -> None:
        self.width, self.height = size
        self.gradient_surface = self._create_gradient_surface()
        self.nodes = self._spawn_nodes()

    def _create_gradient_surface(self) -> pygame.Surface:
        gradient = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            mix = y / self.height
            color = [
                int(COLORS.background_top[i] * (1 - mix) + COLORS.background_bottom[i] * mix)
                for i in range(3)
            ]
            pygame.draw.line(gradient, color, (0, y), (self.width, y))
        gradient.set_alpha(230)
        return gradient

    def _spawn_nodes(self) -> List[FloatingNode]:
        nodes: List[FloatingNode] = []
        for _ in range(24):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            angle = random.uniform(0, 360)
            speed = random.uniform(15, 35)
            velocity = pygame.math.Vector2(speed, 0).rotate(angle)
            base_radius = random.uniform(10, 22)
            color = COLORS.accent if random.random() > 0.5 else COLORS.accent_secondary
            nodes.append(
                FloatingNode(
                    position=pygame.math.Vector2(x, y),
                    velocity=velocity,
                    radius=base_radius,
                    base_radius=base_radius,
                    color=color,
                )
            )
        return nodes

    def update(self, dt: float) -> None:
        for node in self.nodes:
            node.update(dt)
            if node.position.x < -40 or node.position.x > self.width + 40:
                node.velocity.x *= -1
            if node.position.y < -40 or node.position.y > self.height + 40:
                node.velocity.y *= -1

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.gradient_surface, (0, 0))
        for node in self.nodes:
            pygame.draw.circle(surface, node.color, node.position, node.radius)
        for node in self.nodes:
            pygame.draw.circle(surface, (255, 255, 255, 40), node.position, node.radius, 1)

