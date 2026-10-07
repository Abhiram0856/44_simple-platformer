import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity = 0.6

        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)

        # A simple hand-built level: platforms with gaps between them
        # (falling into a gap means falling off the bottom of the
        # screen), one hazard, and a goal near the right edge.
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        self.hazards = [Hazard(240, ground_y - 14, 100)]
        self.goal_x = 740

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 64)
        self.game_over_instruction_font = pygame.font.SysFont("Arial", 26)
        self.game_over = False
        self.exit_requested = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Once the game is over, wait for the player's input instead
        # of continuing normal gameplay.
        if self.game_over:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.exit_requested = True
            return

        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        if self.game_over:
            self.player.vx = 0
            return

        keys = pygame.key.get_pressed()
        self.player.vx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        if self.game_over:
            return

        # Remember the previous vertical position so we can detect
        # crossing a platform even when falling quickly.
        previous_y = self.player.y

        self.player.vy += self.gravity
        self.player.x = max(0, self.player.x + self.player.vx)
        self.player.y += self.player.vy
        self.player.on_ground = False

        # Reliable platform collision: detect when the player's
        # bottom crosses the top of a platform while descending.
        for platform in self.platforms:
            if self.player.vy >= 0:
                player_bottom_previous = previous_y + self.player.height
                player_bottom_current = self.player.y + self.player.height

                crossed_platform = (
                    player_bottom_previous <= platform.y
                    and player_bottom_current >= platform.y
                )

                horizontal_overlap = (
                    self.player.x < platform.x + platform.width
                    and self.player.x + self.player.width > platform.x
                )

                if crossed_platform and horizontal_overlap:
                    self.player.y = platform.y - self.player.height
                    self.player.vy = 0
                    self.player.on_ground = True
                    break

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                return

        if self.player.y > self.height:
            self.game_over = True
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())

        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            # Display the final result inside the game window rather
            # than printing it to the console.
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            game_over_text = self.game_over_font.render(
                "GAME OVER",
                True,
                WHITE
            )
            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )
            instruction_text = self.game_over_instruction_font.render(
                "Press Enter or Esc to exit",
                True,
                WHITE
            )

            screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 80)
                )
            )

            screen.blit(
                final_score_text,
                final_score_text.get_rect(
                    center=(self.width // 2, self.height // 2)
                )
            )

            screen.blit(
                instruction_text,
                instruction_text.get_rect(
                    center=(self.width // 2, self.height // 2 + 60)
                )
            )
