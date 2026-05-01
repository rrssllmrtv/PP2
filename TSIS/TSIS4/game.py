# game.py
import pygame
import random
import json
import os
from db import save_result, get_personal_best

pygame.init()

WIDTH, HEIGHT = 800, 600
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake TSIS4")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Verdana", 22)
small_font = pygame.font.SysFont("Verdana", 16)
big_font = pygame.font.SysFont("Verdana", 45)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (80, 80, 80)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
BLUE = (0, 120, 255)
YELLOW = (230, 210, 0)
CYAN = (0, 200, 200)
BROWN = (100, 60, 20)

SETTINGS_FILE = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        data = {
            "snake_color": [0, 180, 0],
            "grid": True
        }
        save_settings(data)
        return data
    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)

settings = load_settings()

def draw_text_center(text, y, size="normal", color=BLACK):
    if size == "big":
        img = big_font.render(text, True, color)
    else:
        img = font.render(text, True, color)
    rect = img.get_rect(center=(WIDTH // 2, y))
    screen.blit(img, rect)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class Food:
    def __init__(self):
        self.weight = 1
        self.image = pygame.Surface((CELL, CELL))
        self.rect = self.image.get_rect()
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 5000

    def new_position(self, snake, obstacles):
        self.weight = random.choice([1, 2, 3])
        if self.weight == 1:
            size = CELL
            color = RED
        elif self.weight == 2:
            size = CELL + 6
            color = ORANGE
        else:
            size = CELL + 10
            color = PURPLE

        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        while True:
            x = random.randrange(CELL, WIDTH - CELL, CELL)
            y = random.randrange(CELL, HEIGHT - CELL, CELL)
            pos = (x, y)
            if pos not in snake and pos not in obstacles:
                self.rect.topleft = pos
                break
        self.spawn_time = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.life_time

    def draw(self):
        screen.blit(self.image, self.rect)


class Poison:
    def __init__(self):
        self.image = pygame.Surface((CELL, CELL))
        self.image.fill(DARK_RED)
        self.rect = self.image.get_rect()

    def new_position(self, snake, obstacles):
        while True:
            x = random.randrange(CELL, WIDTH - CELL, CELL)
            y = random.randrange(CELL, HEIGHT - CELL, CELL)
            pos = (x, y)
            if pos not in snake and pos not in obstacles:
                self.rect.topleft = pos
                break

    def draw(self):
        pygame.draw.rect(screen, DARK_RED, self.rect)


class PowerUp:
    def __init__(self):
        self.kind = None
        self.rect = pygame.Rect(0, 0, CELL, CELL)
        self.spawn_time = 0
        self.life_time = 8000
        self.active = False

    def spawn(self, snake, obstacles):
        self.kind = random.choice(["speed", "slow", "shield"])
        self.active = True
        self.spawn_time = pygame.time.get_ticks()
        while True:
            x = random.randrange(CELL, WIDTH - CELL, CELL)
            y = random.randrange(CELL, HEIGHT - CELL, CELL)
            pos = (x, y)
            if pos not in snake and pos not in obstacles:
                self.rect.topleft = pos
                break

    def expired(self):
        return self.active and pygame.time.get_ticks() - self.spawn_time >= self.life_time

    def draw(self):
        if not self.active:
            return
        if self.kind == "speed":
            color = BLUE
        elif self.kind == "slow":
            color = YELLOW
        else:
            color = CYAN
        pygame.draw.rect(screen, color, self.rect)


class Game:
    def __init__(self, username):
        self.username = username
        self.personal_best = get_personal_best(username)
        self.reset()

    def reset(self):
        self.snake = [(400, 300), (380, 300), (360, 300)]
        self.dx = CELL
        self.dy = 0
        self.score = 0
        self.level = 1
        self.food_count = 0
        self.base_speed = 8
        self.speed = self.base_speed
        self.obstacles = []
        self.food = Food()
        self.food.new_position(self.snake, self.obstacles)
        self.poison = Poison()
        self.poison.new_position(self.snake, self.obstacles)
        self.power = PowerUp()
        self.last_power_spawn = pygame.time.get_ticks()
        self.speed_boost_until = 0
        self.slow_until = 0
        self.shield = False
        self.game_over = False
        self.saved = False

    def generate_obstacles(self):
        self.obstacles = []
        count = min(8 + self.level * 2, 35)
        head = self.snake[0]
        forbidden = set(self.snake)
        forbidden.add((head[0] + CELL, head[1]))
        forbidden.add((head[0] - CELL, head[1]))
        forbidden.add((head[0], head[1] + CELL))
        forbidden.add((head[0], head[1] - CELL))
        while len(self.obstacles) < count:
            x = random.randrange(CELL * 2, WIDTH - CELL * 2, CELL)
            y = random.randrange(CELL * 2, HEIGHT - CELL * 2, CELL)
            pos = (x, y)
            if pos not in forbidden and pos not in self.obstacles:
                self.obstacles.append(pos)

    def handle_key(self, key):
        if key == pygame.K_UP and self.dy == 0:
            self.dx = 0
            self.dy = -CELL
        elif key == pygame.K_DOWN and self.dy == 0:
            self.dx = 0
            self.dy = CELL
        elif key == pygame.K_LEFT and self.dx == 0:
            self.dx = -CELL
            self.dy = 0
        elif key == pygame.K_RIGHT and self.dx == 0:
            self.dx = CELL
            self.dy = 0

    def update_power_effects(self):
        now = pygame.time.get_ticks()
        self.speed = self.base_speed
        if now < self.speed_boost_until:
            self.speed = self.base_speed + 5
        if now < self.slow_until:
            self.speed = max(4, self.base_speed - 4)

    def update(self):
        if self.game_over:
            if not self.saved:
                save_result(self.username, self.score, self.level)
                self.personal_best = max(self.personal_best, self.score)
                self.saved = True
            return

        now = pygame.time.get_ticks()
        if self.food.expired():
            self.food.new_position(self.snake, self.obstacles)
        if self.power.expired():
            self.power.active = False
        if not self.power.active and now - self.last_power_spawn >= 7000:
            self.power.spawn(self.snake, self.obstacles)
            self.last_power_spawn = now

        self.update_power_effects()

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.dx, head_y + self.dy)

        collision = (
            new_head[0] < CELL or new_head[0] >= WIDTH - CELL or
            new_head[1] < CELL or new_head[1] >= HEIGHT - CELL or
            new_head in self.snake or new_head in self.obstacles
        )

        if collision:
            if self.shield:
                self.shield = False
                return
            else:
                self.game_over = True
                return

        self.snake.insert(0, new_head)

        ate_food = new_head == self.food.rect.topleft
        ate_poison = new_head == self.poison.rect.topleft
        ate_power = self.power.active and new_head == self.power.rect.topleft

        if ate_food:
            self.score += self.food.weight
            self.food_count += 1
            self.food.new_position(self.snake, self.obstacles)
            if self.food_count == 3:
                self.level += 1
                self.base_speed += 2
                self.food_count = 0
                if self.level >= 3:
                    self.generate_obstacles()
                    self.food.new_position(self.snake, self.obstacles)
                    self.poison.new_position(self.snake, self.obstacles)
        elif ate_poison:
            self.snake.pop()
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            self.poison.new_position(self.snake, self.obstacles)
            if len(self.snake) <= 1:
                self.game_over = True
        else:
            self.snake.pop()

        if ate_power:
            if self.power.kind == "speed":
                self.speed_boost_until = pygame.time.get_ticks() + 5000
            elif self.power.kind == "slow":
                self.slow_until = pygame.time.get_ticks() + 5000
            elif self.power.kind == "shield":
                self.shield = True
            self.power.active = False

    def draw_grid(self):
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    def draw_border(self):
        for x in range(0, WIDTH, CELL):
            pygame.draw.rect(screen, BLACK, (x, 0, CELL, CELL))
            pygame.draw.rect(screen, BLACK, (x, HEIGHT - CELL, CELL, CELL))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.rect(screen, BLACK, (0, y, CELL, CELL))
            pygame.draw.rect(screen, BLACK, (WIDTH - CELL, y, CELL, CELL))

    def draw(self):
        screen.fill(WHITE)
        if settings["grid"]:
            self.draw_grid()
        self.draw_border()

        for block in self.obstacles:
            pygame.draw.rect(screen, BROWN, (block[0], block[1], CELL, CELL))

        self.food.draw()
        self.poison.draw()
        self.power.draw()

        snake_color = tuple(settings["snake_color"])
        for part in self.snake:
            pygame.draw.rect(screen, snake_color, (part[0], part[1], CELL, CELL))

        texts = [
            "Player: " + self.username,
            "Score: " + str(self.score),
            "Level: " + str(self.level),
            "Best: " + str(self.personal_best),
            "Food: +" + str(self.food.weight),
            "Shield: " + ("YES" if self.shield else "NO")
        ]
        y = 25
        for text in texts:
            img = small_font.render(text, True, BLACK)
            screen.blit(img, (25, y))
            y += 24