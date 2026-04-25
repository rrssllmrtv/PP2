import pygame, random, time
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()

RED = (255, 0, 0)
BLACK = (0, 0, 0)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        self.image = pygame.transform.scale(self.original_image, (30, 30))
        self.rect = self.image.get_rect()
        self.active = False

    def spawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -30)
        self.active = True

    def move(self):
        if self.active:
            self.rect.move_ip(0, SPEED)

            if self.rect.top > SCREEN_HEIGHT:
                self.active = False

    def draw_if_active(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


player = Player()
enemy = Enemy()
coin = Coin()

enemies = pygame.sprite.Group()
enemies.add(enemy)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemy)

INC_SPEED = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2

pygame.time.set_timer(INC_SPEED, 1000)
pygame.time.set_timer(SPAWN_COIN, 1000)

done = True

while done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = False

        if event.type == INC_SPEED:
            SPEED += 0.2

        if event.type == SPAWN_COIN:
            if not coin.active:
                coin.spawn()

    screen.blit(background, (0, 0))

    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    screen.blit(score_text, (10, 10))

    coins_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)
    coins_rect = coins_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    screen.blit(coins_text, coins_rect)

    for entity in all_sprites:
        entity.move()
        screen.blit(entity.image, entity.rect)

    coin.move()
    coin.draw_if_active(screen)

    if coin.active and pygame.sprite.collide_rect(player, coin):
        COINS_COLLECTED += 1
        coin.active = False

    if pygame.sprite.spritecollideany(player, enemies):
        screen.fill(RED)
        screen.blit(game_over_text, game_over_rect)
        pygame.display.update()
        time.sleep(1)
        done = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()