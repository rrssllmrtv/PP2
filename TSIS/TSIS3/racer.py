import pygame
import random
import os
import time
from constants import (
    WIDTH, HEIGHT,
    WHITE, BLACK, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE,
    LANES, ROAD_LEFT, ROAD_RIGHT, FINISH_DISTANCE,
    screen, font_small,
)


def load_image(name, size=None, alpha=True):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "assets", name)

    if not os.path.exists(path):
        print("Файл не найден:", path)
        return None

    img = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()

    if size:
        img = pygame.transform.scale(img, size)

    return img


class Player(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.original_image = load_image("Player.png", (45, 75))

        if self.original_image is None:
            self.original_image = pygame.Surface((45, 75), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, BLUE, (7, 5, 31, 65), border_radius=8)
            pygame.draw.rect(self.original_image, BLACK, (7, 5, 31, 65), 2, border_radius=8)

        self.image = self.original_image.copy()
        self.apply_color()

        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, 590)

        self.speed = 6
        self.shield = False

    def apply_color(self):
        if self.settings["car_color"] == "original":
            return
        colors = {"blue": BLUE, "red": RED, "green": GREEN, "purple": PURPLE}
        color = colors.get(self.settings["car_color"], BLUE)

        overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        overlay.fill((color[0], color[1], color[2], 90))
        self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > ROAD_LEFT:   self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:             self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:   self.rect.y += self.speed


class TrafficCar(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = load_image("Enemy.png", (45, 75))
        if self.image is None:
            self.image = pygame.Surface((45, 75), pygame.SRCALPHA)
            pygame.draw.rect(self.image, RED, (0, 0, 45, 75), border_radius=8)

        self.rect = self.image.get_rect()
        self.speed = speed
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-500, -80)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.original = load_image("coin.png", (35, 35))
        if self.original is None:
            self.original = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(self.original, YELLOW, (17, 17), 17)
            pygame.draw.circle(self.original, BLACK, (17, 17), 17, 2)

        self.weight = random.choice([1, 2, 3])
        size = 28 if self.weight == 1 else 36 if self.weight == 2 else 44
        self.image = pygame.transform.scale(self.original, (size, size))
        self.rect = self.image.get_rect()

        self.speed = speed
        self.spawn_time = time.time()
        self.timeout = 5
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-500, -80)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT or time.time() - self.spawn_time > self.timeout:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(["barrier", "oil", "pothole"])
        self.image = pygame.Surface((60, 35), pygame.SRCALPHA)

        if self.kind == "barrier":
            pygame.draw.rect(self.image, ORANGE, (0, 0, 60, 35), border_radius=6)
            pygame.draw.rect(self.image, BLACK, (0, 0, 60, 35), 2, border_radius=6)
        elif self.kind == "oil":
            pygame.draw.ellipse(self.image, BLACK, (0, 5, 60, 25))
            pygame.draw.ellipse(self.image, DARK_GRAY, (10, 10, 40, 12))
        else:
            pygame.draw.ellipse(self.image, DARK_GRAY, (0, 0, 60, 35))
            pygame.draw.ellipse(self.image, BLACK, (10, 8, 40, 20))

        self.rect = self.image.get_rect()
        self.speed = speed
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-500, -80)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(["nitro", "shield", "repair"])
        self.image = pygame.Surface((38, 38), pygame.SRCALPHA)

        if self.kind == "nitro":   color, letter = BLUE, "N"
        elif self.kind == "shield": color, letter = PURPLE, "S"
        else:                      color, letter = GREEN, "R"

        pygame.draw.circle(self.image, color, (19, 19), 19)
        pygame.draw.circle(self.image, BLACK, (19, 19), 19, 2)
        text = font_small.render(letter, True, WHITE)
        self.image.blit(text, text.get_rect(center=(19, 19)))

        self.rect = self.image.get_rect()
        self.speed = speed
        self.spawn_time = time.time()
        self.timeout = 6

        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-550, -100)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT or time.time() - self.spawn_time > self.timeout:
            self.kill()


class Game:
    def __init__(self, username, settings):
        self.username = username
        self.settings = settings
        self.player = Player(settings)

        self.traffic = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.coins_collected = 0
        self.distance = 0
        self.bonus_score = 0
        self.score = 0

        self.base_speed = 5
        self.road_speed = 5

        self.game_over = False
        self.finished = False

        self.active_power = None
        self.active_power_end = 0

        self.traffic_timer = 0
        self.coin_timer = 0
        self.obstacle_timer = 0
        self.powerup_timer = 0

        if settings["difficulty"] == "easy":
            self.difficulty_mult = 0.75
        elif settings["difficulty"] == "hard":
            self.difficulty_mult = 1.3
        else:
            self.difficulty_mult = 1.0

        self.background = load_image("AnimatedStreet.png", (WIDTH, HEIGHT), alpha=False)

    def spawn_safe(self, group, obj):
        if obj.rect.colliderect(self.player.rect):
            obj.kill()
            return
        for item in group:
            if item != obj and obj.rect.colliderect(item.rect):
                obj.kill()
                return

    def update_power_time(self):
        if self.active_power == "nitro" and time.time() >= self.active_power_end:
            self.active_power = None
            self.road_speed = self.base_speed

    def activate_power(self, kind):
        if self.active_power is not None:
            return
        if kind == "nitro":
            self.active_power = "nitro"
            self.active_power_end = time.time() + 4
            self.road_speed = self.base_speed + 4
            self.bonus_score += 50
        elif kind == "shield":
            self.active_power = "shield"
            self.player.shield = True
            self.bonus_score += 30
        elif kind == "repair":
            if self.obstacles:
                list(self.obstacles)[0].kill()
            self.bonus_score += 40

    def crash(self, obj=None):
        if self.player.shield:
            if isinstance(obj, TrafficCar) or (isinstance(obj, Obstacle) and obj.kind == "barrier"):
                self.player.shield = False
                self.active_power = None
                if obj:
                    obj.kill()
                self.player.rect.y += 40
                return

        if isinstance(obj, Obstacle):
            if obj.kind == "oil":
                self.player.rect.x += random.choice([-25, 25])
                obj.kill()
                return
            elif obj.kind == "pothole":
                self.road_speed = max(3, self.road_speed - 2)
                obj.kill()
                return

        self.game_over = True

    def update_score(self):
        self.score = int(self.distance + self.coins_collected * 20 + self.bonus_score)

    def update(self):
        self.player.move()
        self.update_power_time()

        self.base_speed = 5 + self.distance / 1250
        if self.active_power != "nitro":
            self.road_speed = self.base_speed

        self.distance += self.road_speed * 0.05

        if FINISH_DISTANCE - self.distance <= 0:
            self.finished = True
            self.game_over = True

        self.traffic_timer += 1
        self.coin_timer += 1
        self.obstacle_timer += 1
        self.powerup_timer += 1

        traffic_delay = max(35, int(95 / self.difficulty_mult - self.distance / 80))
        obstacle_delay = max(45, int(140 / self.difficulty_mult - self.distance / 70))

        if self.traffic_timer >= traffic_delay:
            self.traffic_timer = 0
            car = TrafficCar(self.road_speed + 1.5)
            self.traffic.add(car)
            self.spawn_safe(self.traffic, car)

        if self.coin_timer >= 80:
            self.coin_timer = 0
            self.coins.add(Coin(self.road_speed))

        if self.obstacle_timer >= obstacle_delay:
            self.obstacle_timer = 0
            obs = Obstacle(self.road_speed)
            self.obstacles.add(obs)
            self.spawn_safe(self.obstacles, obs)

        if self.powerup_timer >= 360:
            self.powerup_timer = 0
            self.powerups.add(PowerUp(self.road_speed))

        self.traffic.update()
        self.coins.update()
        self.obstacles.update()
        self.powerups.update()

        for coin in pygame.sprite.spritecollide(self.player, self.coins, True):
            self.coins_collected += coin.weight

        for power in pygame.sprite.spritecollide(self.player, self.powerups, True):
            self.activate_power(power.kind)

        hit_car = pygame.sprite.spritecollideany(self.player, self.traffic)
        if hit_car:
            self.crash(hit_car)

        hit_obstacle = pygame.sprite.spritecollideany(self.player, self.obstacles)
        if hit_obstacle:
            self.crash(hit_obstacle)

        self.update_score()

    def draw_road(self):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((30, 130, 30))
            pygame.draw.rect(screen, DARK_GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
            for y in range(0, HEIGHT, 80):
                pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 5, y, 10, 40))
            pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
            pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    def draw(self):
        self.draw_road()
        self.coins.draw(screen)
        self.powerups.draw(screen)
        self.obstacles.draw(screen)
        self.traffic.draw(screen)

        screen.blit(self.player.image, self.player.rect)

        if self.player.shield:
            pygame.draw.circle(screen, PURPLE, self.player.rect.center, 48, 3)

        remaining = max(0, FINISH_DISTANCE - self.distance)
        screen.blit(font_small.render(f"Score: {int(self.score)}", True, BLACK), (10, 10))
        screen.blit(font_small.render(f"Coins: {self.coins_collected}", True, BLACK), (10, 35))
        screen.blit(font_small.render(f"Distance: {int(self.distance)} m", True, BLACK), (10, 60))
        screen.blit(font_small.render(f"Left: {int(remaining)} m", True, BLACK), (10, 85))

        if self.active_power == "nitro":
            left = max(0, int(self.active_power_end - time.time()))
            txt = f"Power: Nitro {left}s"
            color = BLUE
        elif self.active_power == "shield":
            txt = "Power: Shield"
            color = PURPLE
        else:
            txt = "Power: none"
            color = BLACK

        screen.blit(font_small.render(txt, True, color), (300, 10))