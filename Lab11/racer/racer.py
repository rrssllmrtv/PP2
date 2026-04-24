import pygame, sys, random
from pygame.locals import *
import time

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

RED = (255, 0, 0)
BLACK = (0, 0, 0)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

SPEED = 5
SCORE = 0
COINS_COLLECTED = 0
COINS_FOR_SPEED = 5

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer with Coins")

font_big = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

game_over_text = font_big.render("Game Over", True, BLACK)
game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

background = pygame.image.load("штуки/AnimatedStreet.png")


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("штуки/Enemy.png")
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("штуки/Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (200, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("штуки/coin.png").convert_alpha()
        self.weight = 1
        self.image = pygame.transform.scale(self.original_image, (30, 30))
        self.rect = self.image.get_rect()
        self.active = False

    def spawn(self, player, enemy):
        self.weight = random.choice([1, 2, 3])

        if self.weight == 1:
            size = 25
        elif self.weight == 2:
            size = 35
        else:
            size = 45

        self.image = pygame.transform.scale(self.original_image, (size, size))
        self.rect = self.image.get_rect()

        while True:
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -30)

            if not self.rect.colliderect(player.rect) and not self.rect.colliderect(enemy.rect):
                break

        self.active = True

    def move(self):
        if self.active:
            self.rect.move_ip(0, SPEED)

            if self.rect.top > SCREEN_HEIGHT:
                self.active = False

    def draw_if_active(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


P1 = Player()
E1 = Enemy()
coin = Coin()

enemies = pygame.sprite.Group()
enemies.add(E1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 1500)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == SPAWN_COIN:
            if not coin.active:
                coin.spawn(P1, E1)

    DISPLAYSURF.blit(background, (0, 0))

    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    coins_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)
    coins_rect = coins_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(coins_text, coins_rect)

    speed_text = font_small.render("Speed: " + str(round(SPEED, 1)), True, BLACK)
    DISPLAYSURF.blit(speed_text, (10, 35))

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    coin.move()
    coin.draw_if_active(DISPLAYSURF)

    if coin.active and pygame.sprite.collide_rect(P1, coin):
        old_coins = COINS_COLLECTED

        COINS_COLLECTED += coin.weight
        coin.active = False
        coin.rect.top = SCREEN_HEIGHT + 100

        if COINS_COLLECTED // COINS_FOR_SPEED > old_coins // COINS_FOR_SPEED:
            SPEED += 1

    if pygame.sprite.spritecollideany(P1, enemies):
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, game_over_rect)
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)