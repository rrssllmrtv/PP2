import pygame
import math

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

font = pygame.font.SysFont("Verdana", 16)


def calculate_rect(start, end):
    x1, y1 = start
    x2, y2 = end

    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x1 - x2)
    height = abs(y1 - y2)

    return pygame.Rect(x, y, width, height)


def calculate_square(start, end):
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        x = x1 - side
    else:
        x = x1

    if y2 < y1:
        y = y1 - side
    else:
        y = y1

    return pygame.Rect(x, y, side, side)


def right_triangle_points(start, end):
    x1, y1 = start
    x2, y2 = end

    return [
        (x1, y1),
        (x1, y2),
        (x2, y2)
    ]


def equilateral_triangle_points(start, end):
    x1, y1 = start
    x2, y2 = end

    side = abs(x2 - x1)
    height = int(side * math.sqrt(3) / 2)

    if y2 < y1:
        height = -height

    return [
        (x1, y1),
        (x2, y1),
        ((x1 + x2) // 2, y1 + height)
    ]


def rhombus_points(start, end):
    x1, y1 = start
    x2, y2 = end

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    return [
        (center_x, y1),
        (x2, center_y),
        (center_x, y2),
        (x1, center_y)
    ]


def draw_smooth_line(surface, draw_color, from_pos, to_pos, size):
    pygame.draw.line(surface, draw_color, from_pos, to_pos, size)
    pygame.draw.circle(surface, draw_color, from_pos, size // 2)
    pygame.draw.circle(surface, draw_color, to_pos, size // 2)


def draw_smooth_polygon(surface, draw_color, points, size):
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        draw_smooth_line(surface, draw_color, start, end, size)


def draw_shape(surface, tool_name, start, end):
    if tool_name == "rectangle":
        rect = calculate_rect(start, end)
        pygame.draw.rect(surface, color, rect, thickness)

    elif tool_name == "circle":
        x1, y1 = start
        x2, y2 = end
        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        pygame.draw.circle(surface, color, start, radius, thickness)

    elif tool_name == "square":
        rect = calculate_square(start, end)
        pygame.draw.rect(surface, color, rect, thickness)

    elif tool_name == "right_triangle":
        points = right_triangle_points(start, end)
        draw_smooth_polygon(surface, color, points, thickness)

    elif tool_name == "equilateral_triangle":
        points = equilateral_triangle_points(start, end)
        draw_smooth_polygon(surface, color, points, thickness)

    elif tool_name == "rhombus":
        points = rhombus_points(start, end)
        draw_smooth_polygon(surface, color, points, thickness)


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
            elif event.key == pygame.K_5:
                tool = "square"
            elif event.key == pygame.K_6:
                tool = "right_triangle"
            elif event.key == pygame.K_7:
                tool = "equilateral_triangle"
            elif event.key == pygame.K_8:
                tool = "rhombus"

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

                else:
                    screen.blit(base_layer, (0, 0))
                    draw_shape(screen, tool, start_pos, current_pos)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                current_pos = event.pos

                if tool != "brush" and tool != "eraser":
                    screen.blit(base_layer, (0, 0))
                    draw_shape(screen, tool, start_pos, current_pos)

                base_layer = screen.copy()

    info = "1 Brush | 2 Rect | 3 Circle | 4 Eraser | 5 Square | 6 Right Tr | 7 Eq Tr | 8 Rhombus | R G B K | +/- | C"
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 30))
    text = font.render(info, True, BLACK)
    screen.blit(text, (10, 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()