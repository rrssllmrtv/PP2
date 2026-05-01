import pygame
import math
from datetime import datetime


def to_canvas_pos(pos, canvas_x):
    x, y = pos
    return x - canvas_x, y


def inside_canvas(pos, canvas_x, width, height):
    x, y = pos
    return x >= canvas_x and 0 <= y < height


def calculate_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    x = min(x1, x2)
    y = min(y1, y2)
    return pygame.Rect(x, y, abs(x1 - x2), abs(y1 - y2))


def calculate_square(start, end):
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))
    x = x1 - side if x2 < x1 else x1
    y = y1 - side if y2 < y1 else y1
    return pygame.Rect(x, y, side, side)


def right_triangle_points(start, end):
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]


def equilateral_triangle_points(start, end):
    x1, y1 = start
    x2, y2 = end
    side = abs(x2 - x1)
    height = int(side * math.sqrt(3) / 2)
    if y2 < y1:
        height = -height
    return [(x1, y1), (x2, y1), ((x1 + x2) // 2, y1 + height)]


def rhombus_points(start, end):
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]


def draw_smooth_line(surface, color, start, end, thickness):
    pygame.draw.line(surface, color, start, end, thickness)
    pygame.draw.circle(surface, color, start, thickness // 2)
    pygame.draw.circle(surface, color, end, thickness // 2)


def draw_smooth_polygon(surface, color, points, thickness):
    for i in range(len(points)):
        draw_smooth_line(surface, color, points[i], points[(i + 1) % len(points)], thickness)


def draw_shape(surface, tool_name, start, end, color, thickness):
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
        if not (0 <= px < width and 0 <= py < height):
            continue
        if surface.get_at((px, py)) != target_color:
            continue
        surface.set_at((px, py), fill_color)
        pixels.append((px + 1, py))
        pixels.append((px - 1, py))
        pixels.append((px, py + 1))
        pixels.append((px, py - 1))


def save_canvas(canvas):
    filename = datetime.now().strftime("paint_%Y-%m-%d_%H-%M-%S.png")
    pygame.image.save(canvas, filename)
    print(f"Saved: {filename}")


def confirm_text(canvas, text_pos, text_value, color, text_font, base_layer):
    if text_pos and text_value.strip():
        text_surface = text_font.render(text_value, True, color)
        canvas.blit(text_surface, text_pos)
    return canvas.copy()