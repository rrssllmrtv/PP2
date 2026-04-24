import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 220)

screen.fill(WHITE)

color = BLACK
tool = "brush"
thickness = 5

drawing = False
start_pos = None
last_pos = None

base_layer = screen.copy()

font = pygame.font.SysFont("Verdana", 18)


def calculate_rect(start, end):
    x1, y1 = start
    x2, y2 = end

    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x1 - x2)
    height = abs(y1 - y2)

    return pygame.Rect(x, y, width, height)


def draw_smooth_line(surface, draw_color, from_pos, to_pos, size):
    pygame.draw.line(surface, draw_color, from_pos, to_pos, size)
    pygame.draw.circle(surface, draw_color, from_pos, size // 2)
    pygame.draw.circle(surface, draw_color, to_pos, size // 2)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_1:
                tool = "brush"
            elif event.key == pygame.K_2:
                tool = "rectangle"
            elif event.key == pygame.K_3:
                tool = "circle"
            elif event.key == pygame.K_4:
                tool = "eraser"

            if event.key == pygame.K_r:
                color = RED
            elif event.key == pygame.K_g:
                color = GREEN
            elif event.key == pygame.K_b:
                color = BLUE
            elif event.key == pygame.K_k:
                color = BLACK

            if event.key == pygame.K_EQUALS:
                thickness += 1
            elif event.key == pygame.K_MINUS:
                thickness = max(1, thickness - 1)

            if event.key == pygame.K_c:
                screen.fill(WHITE)
                base_layer = screen.copy()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos
                base_layer = screen.copy()

        if event.type == pygame.MOUSEMOTION:
            if drawing:
                current_pos = event.pos

                if tool == "brush":
                    draw_smooth_line(screen, color, last_pos, current_pos, thickness)
                    last_pos = current_pos
                    base_layer = screen.copy()

                elif tool == "eraser":
                    draw_smooth_line(screen, WHITE, last_pos, current_pos, thickness)
                    last_pos = current_pos
                    base_layer = screen.copy()

                elif tool == "rectangle":
                    screen.blit(base_layer, (0, 0))
                    rect = calculate_rect(start_pos, current_pos)
                    pygame.draw.rect(screen, color, rect, thickness)

                elif tool == "circle":
                    screen.blit(base_layer, (0, 0))
                    x1, y1 = start_pos
                    x2, y2 = current_pos
                    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                    pygame.draw.circle(screen, color, start_pos, radius, thickness)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                current_pos = event.pos

                if tool == "rectangle":
                    screen.blit(base_layer, (0, 0))
                    rect = calculate_rect(start_pos, current_pos)
                    pygame.draw.rect(screen, color, rect, thickness)

                elif tool == "circle":
                    screen.blit(base_layer, (0, 0))
                    x1, y1 = start_pos
                    x2, y2 = current_pos
                    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                    pygame.draw.circle(screen, color, start_pos, radius, thickness)

                base_layer = screen.copy()

    info = "1 Brush | 2 Rectangle | 3 Circle | 4 Eraser | R G B K colors | +/- size | C clear"
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 30))
    text = font.render(info, True, BLACK)
    screen.blit(text, (10, 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()