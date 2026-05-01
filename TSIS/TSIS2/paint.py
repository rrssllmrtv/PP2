import pygame
import math
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 900, 550
PANEL_WIDTH = 260
CANVAS_X = PANEL_WIDTH
CANVAS_WIDTH = WIDTH - PANEL_WIDTH
CANVAS_HEIGHT = HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint TSIS2")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 230)
DARK_GRAY = (80, 80, 80)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 220)

canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)

color = BLACK
tool = "pencil"
thickness = 5

drawing = False
start_pos = None
last_pos = None
base_layer = canvas.copy()

text_mode = False
text_pos = None
text_value = ""

font = pygame.font.SysFont("Verdana", 15)
small_font = pygame.font.SysFont("Verdana", 13)
text_font = pygame.font.SysFont("Verdana", 28)


def to_canvas_pos(pos):
    x, y = pos
    return x - CANVAS_X, y


def inside_canvas(pos):
    x, y = pos
    return x >= CANVAS_X and 0 <= y < HEIGHT


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
    if tool_name == "line":
        draw_smooth_line(surface, color, start, end, thickness)

    elif tool_name == "rectangle":
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


def flood_fill(surface, x, y, fill_color):
    width, height = surface.get_size()

    if x < 0 or x >= width or y < 0 or y >= height:
        return

    target_color = surface.get_at((x, y))
    fill_color = pygame.Color(fill_color)

    if target_color == fill_color:
        return

    pixels = [(x, y)]

    while pixels:
        px, py = pixels.pop()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), fill_color)

        pixels.append((px + 1, py))
        pixels.append((px - 1, py))
        pixels.append((px, py + 1))
        pixels.append((px, py - 1))


def save_canvas():
    filename = datetime.now().strftime("paint_%Y-%m-%d_%H-%M-%S.png")
    pygame.image.save(canvas, filename)
    print("Saved:", filename)


def confirm_text():
    global text_mode, text_value, text_pos, base_layer

    if text_pos is not None and text_value != "":
        text_surface = text_font.render(text_value, True, color)
        canvas.blit(text_surface, text_pos)

    base_layer = canvas.copy()
    text_mode = False
    text_value = ""
    text_pos = None


def cancel_text():
    global text_mode, text_value, text_pos

    canvas.blit(base_layer, (0, 0))
    text_mode = False
    text_value = ""
    text_pos = None


def draw_panel():
    pygame.draw.rect(screen, GRAY, (0, 0, PANEL_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (PANEL_WIDTH, 0), (PANEL_WIDTH, HEIGHT), 2)

    y = 12

    title = font.render("PAINT TSIS2", True, BLACK)
    screen.blit(title, (15, y))
    y += 32

    current = small_font.render(f"Tool: {tool}", True, BLACK)
    screen.blit(current, (15, y))
    y += 22

    size_text = small_font.render(f"Size: {thickness}px", True, BLACK)
    screen.blit(size_text, (15, y))
    y += 22

    color_text = small_font.render("Color:", True, BLACK)
    screen.blit(color_text, (15, y))
    pygame.draw.rect(screen, color, (75, y - 2, 28, 18))
    pygame.draw.rect(screen, BLACK, (75, y - 2, 28, 18), 1)

    y += 35

    tools_title = small_font.render("TOOLS", True, BLACK)
    screen.blit(tools_title, (15, y))
    y += 22

    left_tools = [
        "P - pencil",
        "L - line",
        "R - rect",
        "O - circle",
        "E - eraser"
    ]

    right_tools = [
        "S - square",
        "A - right triangle",
        "Q - equiv triangle",
        "D - rhombus",
        "F - fill",
        "T - text"
    ]

    start_y = y

    for line in left_tools:
        text = small_font.render(line, True, DARK_GRAY)
        screen.blit(text, (15, y))
        y += 20

    y = start_y

    for line in right_tools:
        text = small_font.render(line, True, DARK_GRAY)
        screen.blit(text, (130, y))
        y += 20

    y = start_y + 125

    size_title = small_font.render("SIZE", True, BLACK)
    screen.blit(size_title, (15, y))
    y += 22

    size_lines = [
        "1 - small(2px)",
        "2 - medium(5px)",
        "3 - large(10px)"
    ]

    for line in size_lines:
        text = small_font.render(line, True, DARK_GRAY)
        screen.blit(text, (15, y))
        y += 20

    y += 10

    color_title = small_font.render("COLORS", True, BLACK)
    screen.blit(color_title, (15, y))
    y += 22

    color_lines_left = [
        "Z - black",
        "X - red"
    ]

    color_lines_right = [
        "V - green",
        "B - blue"
    ]

    start_y = y

    for line in color_lines_left:
        text = small_font.render(line, True, DARK_GRAY)
        screen.blit(text, (15, y))
        y += 20

    y = start_y

    for line in color_lines_right:
        text = small_font.render(line, True, DARK_GRAY)
        screen.blit(text, (130, y))
        y += 20

    y = start_y + 55

    other_title = small_font.render("OTHER", True, BLACK)
    screen.blit(other_title, (15, y))
    y += 22

    other_lines = [
        "C - clear",
        "Ctrl+S - save canvas",
        "Esc - exit / cancel text",
        "Enter - confirm text"
    ]

    for line in other_lines:
        text = small_font.render(line, True, DARK_GRAY)
        screen.blit(text, (15, y))
        y += 20


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if text_mode:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    confirm_text()

                elif event.key == pygame.K_ESCAPE:
                    cancel_text()

                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]

                elif event.unicode != "":
                    text_value += event.unicode

            else:
                if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_s:
                    save_canvas()

                elif event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_p:
                    tool = "pencil"
                elif event.key == pygame.K_l:
                    tool = "line"
                elif event.key == pygame.K_r:
                    tool = "rectangle"
                elif event.key == pygame.K_o:
                    tool = "circle"
                elif event.key == pygame.K_e:
                    tool = "eraser"
                elif event.key == pygame.K_s:
                    tool = "square"
                elif event.key == pygame.K_a:
                    tool = "right_triangle"
                elif event.key == pygame.K_q:
                    tool = "equilateral_triangle"
                elif event.key == pygame.K_d:
                    tool = "rhombus"
                elif event.key == pygame.K_f:
                    tool = "fill"
                elif event.key == pygame.K_t:
                    tool = "text"

                elif event.key == pygame.K_1:
                    thickness = 2
                elif event.key == pygame.K_2:
                    thickness = 5
                elif event.key == pygame.K_3:
                    thickness = 10

                elif event.key == pygame.K_z:
                    color = BLACK
                elif event.key == pygame.K_x:
                    color = RED
                elif event.key == pygame.K_v:
                    color = GREEN
                elif event.key == pygame.K_b:
                    color = BLUE

                elif event.key == pygame.K_c:
                    canvas.fill(WHITE)
                    base_layer = canvas.copy()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and inside_canvas(event.pos):
                canvas_pos = to_canvas_pos(event.pos)

                if tool == "fill":
                    flood_fill(canvas, canvas_pos[0], canvas_pos[1], color)
                    base_layer = canvas.copy()

                elif tool == "text":
                    if text_mode:
                        confirm_text()

                    text_mode = True
                    text_pos = canvas_pos
                    text_value = ""
                    base_layer = canvas.copy()

                else:
                    drawing = True
                    start_pos = canvas_pos
                    last_pos = canvas_pos
                    base_layer = canvas.copy()

        if event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                current_pos = to_canvas_pos(event.pos)

                if tool == "pencil":
                    draw_smooth_line(canvas, color, last_pos, current_pos, thickness)
                    last_pos = current_pos
                    base_layer = canvas.copy()

                elif tool == "eraser":
                    draw_smooth_line(canvas, WHITE, last_pos, current_pos, thickness)
                    last_pos = current_pos
                    base_layer = canvas.copy()

                else:
                    canvas.blit(base_layer, (0, 0))
                    draw_shape(canvas, tool, start_pos, current_pos)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False

                if inside_canvas(event.pos):
                    current_pos = to_canvas_pos(event.pos)

                    if tool != "pencil" and tool != "eraser":
                        canvas.blit(base_layer, (0, 0))
                        draw_shape(canvas, tool, start_pos, current_pos)

                base_layer = canvas.copy()

    if text_mode and text_pos is not None:
        canvas.blit(base_layer, (0, 0))
        text_surface = text_font.render(text_value, True, color)
        canvas.blit(text_surface, text_pos)

        cursor_x = text_pos[0] + text_surface.get_width() + 2
        cursor_y = text_pos[1]
        pygame.draw.line(canvas, color, (cursor_x, cursor_y), (cursor_x, cursor_y + 28), 2)

    screen.fill(WHITE)
    screen.blit(canvas, (CANVAS_X, 0))
    draw_panel()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()