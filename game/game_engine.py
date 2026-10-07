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
        self.difficulties = {
            "Easy": {"gravity": 0.45, "jump_strength": -13},
            "Medium": {"gravity": 0.6, "jump_strength": -12},
            "Hard": {"gravity": 0.85, "jump_strength": -11},
        }
        self.difficulty = "Medium"
        self.gravity = self.difficulties[self.difficulty]["gravity"]

        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)

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
        self.difficulty_font = pygame.font.SysFont("Arial", 30)
        self.game_over = False
        self.exit_requested = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            if event.key in (pygame.K_1, pygame.K_e):
                self.restart("Easy")
            elif event.key in (pygame.K_2, pygame.K_m):
                self.restart("Medium")
            elif event.key in (pygame.K_3, pygame.K_h):
                self.restart("Hard")
            elif event.key in (pygame.K_x, pygame.K_ESCAPE):
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

    def restart(self, difficulty):
        settings = self.difficulties[difficulty]
        self.difficulty = difficulty
        self.gravity = settings["gravity"]

        self.player.x = self.start_x
        self.player.y = self.start_y
        self.player.vx = 0
        self.player.vy = 0
        self.player.jump_strength = settings["jump_strength"]
        self.player.on_ground = False

        self.score = 0
        self.game_over = False
        self.exit_requested = False

    def update(self):
        if self.game_over:
            return

        previous_y = self.player.y

        self.player.vy += self.gravity
        self.player.x = max(0, self.player.x + self.player.vx)
        self.player.y += self.player.vy
        self.player.on_ground = False

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

        difficulty_text = self.difficulty_font.render(
            f"Difficulty: {self.difficulty}",
            True,
            WHITE
        )
        screen.blit(difficulty_text, (10, 45))

        if self.game_over:
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
            difficulty_text = self.difficulty_font.render(
                "1/E: Easy    2/M: Medium    3/H: Hard",
                True,
                WHITE
            )
            exit_text = self.game_over_instruction_font.render(
                "X or Esc: Exit",
                True,
                WHITE
            )

            screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 110)
                )
            )

            screen.blit(
                final_score_text,
                final_score_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 35)
                )
            )

            screen.blit(
                difficulty_text,
                difficulty_text.get_rect(
                    center=(self.width // 2, self.height // 2 + 35)
                )
            )

            screen.blit(
                exit_text,
                exit_text.get_rect(
                    center=(self.width // 2, self.height // 2 + 85)
                )
            )
