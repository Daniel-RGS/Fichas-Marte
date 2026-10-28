from .environment import AutonomousRallyEnv


def run():
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("Instala pygame con: pip install pygame") from exc
    pygame.init()
    screen = pygame.display.set_mode((900, 240))
    clock = pygame.time.Clock()
    env = AutonomousRallyEnv(); state, _ = env.reset()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
        action = 0 if env.speed < 2 else 1
        state, _, terminated, truncated, _ = env.step(action)
        screen.fill((25, 40, 55))
        pygame.draw.rect(screen, (70, 70, 70), (30, 90, 840, 60))
        x = 30 + int(840 * env.position / (env.track_length - 1))
        pygame.draw.circle(screen, (255, 120, 20), (x, 120), 14)
        pygame.display.flip(); clock.tick(8)
        if terminated or truncated: state, _ = env.reset()
    pygame.quit()

