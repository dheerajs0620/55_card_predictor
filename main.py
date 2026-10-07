import pygame
from game.game_engine import GameEngine

WIDTH, HEIGHT = 650, 440
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("High-Low Card Predictor - Pygame Edition")
    clock = pygame.time.Clock()

    engine = GameEngine(WIDTH, HEIGHT)

    dt = 0  # TASK 4: ms elapsed in the previous frame, drives the reveal timer
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            engine.handle_event(event)

        engine.update(dt)  # TASK 4: pass frame time so the engine can time the reveal
        engine.render(screen)

        pygame.display.flip()
        dt = clock.tick(FPS)  # TASK 4: capture the frame time instead of discarding it

    pygame.quit()


if __name__ == "__main__":
    main()