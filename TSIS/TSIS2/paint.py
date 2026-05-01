import pygame
from tools import *

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
base_layer = canvas.copy()

color = BLACK
tool = "pencil"
thickness = 5
drawing = False
start_pos = None
last_pos = None

text_mode = False
text_pos = None
text_value = ""

font = pygame.font.SysFont("Verdana", 15)
small_font = pygame.font.SysFont("Verdana", 13)
text_font = pygame.font.SysFont("Verdana", 28)


def draw_panel():
    pygame.draw.rect(screen, GRAY, (0, 0, PANEL_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (PANEL_WIDTH, 0), (PANEL_WIDTH, HEIGHT), 2)

    y = 12
    screen.blit(font.render("PAINT TSIS2", True, BLACK), (15, y))
    y += 32

    screen.blit(small_font.render(f"Tool: {tool}", True, BLACK), (15, y))
    y += 22
    screen.blit(small_font.render(f"Size: {thickness}px", True, BLACK), (15, y))
    y += 22

    screen.blit(small_font.render("Color:", True, BLACK), (15, y))
    pygame.draw.rect(screen, color, (75, y - 2, 28, 18))
    pygame.draw.rect(screen, BLACK, (75, y - 2, 28, 18), 1)
    y += 35

    screen.blit(small_font.render("TOOLS", True, BLACK), (15, y))
    y += 22
    left = ["P - pencil", "L - line", "R - rect", "O - circle", "E - eraser"]
    right = ["S - square", "A - right triangle", "Q - equiv triangle",
             "D - rhombus", "F - fill", "T - text"]

    start_y = y
    for line in left:
        screen.blit(small_font.render(line, True, DARK_GRAY), (15, y))
        y += 20
    y = start_y
    for line in right:
        screen.blit(small_font.render(line, True, DARK_GRAY), (130, y))
        y += 20

    y = start_y + 125
    screen.blit(small_font.render("SIZE", True, BLACK), (15, y))
    y += 22
    for line in ["1 - small(2px)", "2 - medium(5px)", "3 - large(10px)"]:
        screen.blit(small_font.render(line, True, DARK_GRAY), (15, y))
        y += 20

    y += 10
    screen.blit(small_font.render("COLORS", True, BLACK), (15, y))
    y += 22
    screen.blit(small_font.render("Z - black", True, DARK_GRAY), (15, y))
    screen.blit(small_font.render("X - red", True, DARK_GRAY), (15, y + 20))
    screen.blit(small_font.render("V - green", True, DARK_GRAY), (130, y))
    screen.blit(small_font.render("B - blue", True, DARK_GRAY), (130, y + 20))

    y += 55
    screen.blit(small_font.render("OTHER", True, BLACK), (15, y))
    y += 22
    other = ["C - clear", "Ctrl+S - save canvas", "Esc - exit / cancel text",
             "Enter - confirm text"]
    for line in other:
        screen.blit(small_font.render(line, True, DARK_GRAY), (15, y))
        y += 20


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if text_mode:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    base_layer = confirm_text(canvas, text_pos, text_value, color, text_font, base_layer)
                    text_mode = False
                    text_value = ""
                    text_pos = None
                elif event.key == pygame.K_ESCAPE:
                    canvas.blit(base_layer, (0, 0))
                    text_mode = False
                    text_value = ""
                    text_pos = None
                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]
                elif event.unicode:
                    text_value += event.unicode
            else:
                if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_s:
                    save_canvas(canvas)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p: tool = "pencil"
                elif event.key == pygame.K_l: tool = "line"
                elif event.key == pygame.K_r: tool = "rectangle"
                elif event.key == pygame.K_o: tool = "circle"
                elif event.key == pygame.K_e: tool = "eraser"
                elif event.key == pygame.K_s: tool = "square"
                elif event.key == pygame.K_a: tool = "right_triangle"
                elif event.key == pygame.K_q: tool = "equilateral_triangle"
                elif event.key == pygame.K_d: tool = "rhombus"
                elif event.key == pygame.K_f: tool = "fill"
                elif event.key == pygame.K_t: tool = "text"
                elif event.key == pygame.K_1: thickness = 2
                elif event.key == pygame.K_2: thickness = 5
                elif event.key == pygame.K_3: thickness = 10
                elif event.key == pygame.K_z: color = BLACK
                elif event.key == pygame.K_x: color = RED
                elif event.key == pygame.K_v: color = GREEN
                elif event.key == pygame.K_b: color = BLUE
                elif event.key == pygame.K_c:
                    canvas.fill(WHITE)
                    base_layer = canvas.copy()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if inside_canvas(event.pos, CANVAS_X, WIDTH, HEIGHT):
                canvas_pos = to_canvas_pos(event.pos, CANVAS_X)

                if tool == "fill":
                    flood_fill(canvas, canvas_pos[0], canvas_pos[1], color)
                    base_layer = canvas.copy()
                elif tool == "text":
                    if text_mode:
                        base_layer = confirm_text(canvas, text_pos, text_value, color, text_font, base_layer)
                    text_mode = True
                    text_pos = canvas_pos
                    text_value = ""
                    base_layer = canvas.copy()
                else:
                    drawing = True
                    start_pos = canvas_pos
                    last_pos = canvas_pos
                    base_layer = canvas.copy()

        if event.type == pygame.MOUSEMOTION and drawing:
            if inside_canvas(event.pos, CANVAS_X, WIDTH, HEIGHT):
                current_pos = to_canvas_pos(event.pos, CANVAS_X)

                if tool in ("pencil", "eraser"):
                    col = WHITE if tool == "eraser" else color
                    draw_smooth_line(canvas, col, last_pos, current_pos, thickness)
                    last_pos = current_pos
                    base_layer = canvas.copy()
                else:
                    canvas.blit(base_layer, (0, 0))
                    draw_shape(canvas, tool, start_pos, current_pos, color, thickness)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
            drawing = False
            if inside_canvas(event.pos, CANVAS_X, WIDTH, HEIGHT):
                current_pos = to_canvas_pos(event.pos, CANVAS_X)
                if tool not in ("pencil", "eraser"):
                    canvas.blit(base_layer, (0, 0))
                    draw_shape(canvas, tool, start_pos, current_pos, color, thickness)
            base_layer = canvas.copy()

    screen.fill(WHITE)
    screen.blit(canvas, (CANVAS_X, 0))

    if text_mode and text_pos is not None:
        text_surface = text_font.render(text_value, True, color)
        text_screen_pos = (text_pos[0] + CANVAS_X, text_pos[1])
        
        screen.blit(text_surface, text_screen_pos)
        
        cursor_x = text_screen_pos[0] + text_surface.get_width() + 2
        cursor_y1 = text_screen_pos[1]
        cursor_y2 = text_screen_pos[1] + text_font.get_height()
        pygame.draw.line(screen, color, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

    draw_panel()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()