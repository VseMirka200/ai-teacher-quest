"""
Точка входа в игру AI Teacher Quest.
"""
from __future__ import annotations

import pygame

from ai.engine import AIEngine
from core.context import GameContext
from core.screen_manager import ScreenManager
from core.settings import WINDOW
from ui.fonts import FontManager


def run_game() -> None:
    pygame.init()

    def set_display(fullscreen: bool) -> pygame.Surface:
        flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
        if fullscreen:
            info = pygame.display.Info()
            size = (info.current_w, info.current_h)
        else:
            size = (WINDOW.width, WINDOW.height)
        surface = pygame.display.set_mode(size, flags)
        caption_suffix = " — полноэкранный режим" if fullscreen else ""
        pygame.display.set_caption(f"{WINDOW.title}{caption_suffix}")
        return surface

    surface = set_display(WINDOW.fullscreen)
    clock = pygame.time.Clock()

    fonts = FontManager()
    ai_engine = AIEngine()
    context = GameContext(
        surface=surface,
        fonts=fonts,
        ai_engine=ai_engine,
        fullscreen=WINDOW.fullscreen,
        screen_size=surface.get_size(),
    )
    context.set_fullscreen_handler(set_display)
    if WINDOW.fullscreen:
        context.apply_fullscreen(True)
    manager = ScreenManager(context)

    running = True
    while running:
        dt = clock.tick(WINDOW.fps) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    manager.go_back()
                elif event.key == pygame.K_F11:
                    context.toggle_fullscreen()
                    manager.handle_resize(context.screen_size)
            elif event.type == pygame.VIDEORESIZE and not context.fullscreen:
                context.surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                context.screen_size = event.size
                manager.handle_resize(event.size)

        manager.update(dt)
        manager.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()

