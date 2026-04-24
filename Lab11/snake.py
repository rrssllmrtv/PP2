import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
CELL = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("snake")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Verdana", 24)
big_font = pygame.font.SysFont("Verdana", 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (220, 0, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)


class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.weight = 1
        self.image = pygame.Surface((CELL, CELL))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 5000

    def new_position(self, snake):
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
            x = random.randrange(CELL * 2, WIDTH - CELL * 2, CELL)
            y = random.randrange(CELL * 2, HEIGHT - CELL * 2, CELL)

            if (x, y) not in snake:
                self.rect.topleft = (x, y)
                break

        self.spawn_time = pygame.time.get_ticks()

    def expired(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.spawn_time >= self.life_time


snake = [(300, 300), (280, 300), (260, 300)]
dx = CELL
dy = 0

food = Food()
food.new_position(snake)

food_group = pygame.sprite.Group()
food_group.add(food)

score = 0
level = 1
food_count = 0
speed = 8

running = True
game_over = False
game_over_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_UP and dy == 0:
                dx = 0
                dy = -CELL
            elif event.key == pygame.K_DOWN and dy == 0:
                dx = 0
                dy = CELL
            elif event.key == pygame.K_LEFT and dx == 0:
                dx = -CELL
                dy = 0
            elif event.key == pygame.K_RIGHT and dx == 0:
                dx = CELL
                dy = 0

    if not game_over:
        if food.expired():
            food.new_position(snake)

        head_x, head_y = snake[0]
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < CELL or
            new_head[0] >= WIDTH - CELL or
            new_head[1] < CELL or
            new_head[1] >= HEIGHT - CELL or
            new_head in snake
        ):
            game_over = True
            game_over_time = pygame.time.get_ticks()
        else:
            snake.insert(0, new_head)

            if new_head == food.rect.topleft:
                score += food.weight
                food_count += 1
                food.new_position(snake)

                if food_count == 3:
                    level += 1
                    speed += 2
                    food_count = 0
            else:
                snake.pop()

    screen.fill(WHITE)

    for x in range(0, WIDTH, CELL):
        pygame.draw.rect(screen, BLACK, (x, 0, CELL, CELL))
        pygame.draw.rect(screen, BLACK, (x, HEIGHT - CELL, CELL, CELL))

    for y in range(0, HEIGHT, CELL):
        pygame.draw.rect(screen, BLACK, (0, y, CELL, CELL))
        pygame.draw.rect(screen, BLACK, (WIDTH - CELL, y, CELL, CELL))

    food_group.draw(screen)

    for part in snake:
        pygame.draw.rect(screen, GREEN, (part[0], part[1], CELL, CELL))

    score_text = font.render("Score: " + str(score), True, BLACK)
    level_text = font.render("Level: " + str(level), True, BLACK)
    weight_text = font.render("Food: +" + str(food.weight), True, BLACK)

    screen.blit(score_text, (25, 25))
    screen.blit(level_text, (25, 55))
    screen.blit(weight_text, (25, 85))

    if game_over:
        text = big_font.render("GAME OVER", True, RED)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)

        if pygame.time.get_ticks() - game_over_time >= 1000:
            running = False

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()