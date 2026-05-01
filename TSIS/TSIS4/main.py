# main.py
import pygame
from game import (
    screen, clock, font, small_font, big_font, WHITE, BLACK, RED,
    settings, draw_text_center, Button, Game, save_settings
)
from db import get_leaderboard, setup_database


def main_menu(username):
    play_btn = Button(300, 260, 200, 45, "Play")
    lb_btn = Button(300, 320, 200, 45, "Leaderboard")
    settings_btn = Button(300, 380, 200, 45, "Settings")
    quit_btn = Button(300, 440, 200, 45, "Quit")

    while True:
        screen.fill(WHITE)
        draw_text_center("SNAKE TSIS4", 90, "big")
        draw_text_center("Enter username:", 150)

        input_rect = pygame.Rect(250, 180, 300, 45)
        pygame.draw.rect(screen, WHITE, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        username_text = font.render(username, True, BLACK)
        text_rect = username_text.get_rect(center=input_rect.center)
        screen.blit(username_text, text_rect)

        play_btn.draw()
        lb_btn.draw()
        settings_btn.draw()
        quit_btn.draw()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", username

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN and username.strip():
                    return "play", username.strip()
                elif len(username) < 15 and event.unicode.isprintable():
                    username += event.unicode

            if play_btn.clicked(event) and username.strip():
                return "play", username.strip()
            if lb_btn.clicked(event):
                return "leaderboard", username
            if settings_btn.clicked(event):
                return "settings", username
            if quit_btn.clicked(event):
                return "quit", username


def leaderboard_screen():
    back_btn = Button(300, 520, 200, 45, "Back")
    rows = get_leaderboard() or []

    while True:
        screen.fill(WHITE)
        draw_text_center("LEADERBOARD", 70, "big")

        headers = ["#", "Username", "Score", "Level", "Date"]
        x_pos = [70, 130, 320, 420, 520]

        for i, header in enumerate(headers):
            img = small_font.render(header, True, BLACK)
            screen.blit(img, (x_pos[i], 130))

        y = 170
        if not rows:
            draw_text_center("No results yet", 250)
        else:
            for index, row in enumerate(rows):
                username, score, level, date = row
                values = [str(index + 1), username, str(score), str(level), date]
                for i, val in enumerate(values):
                    img = small_font.render(val, True, BLACK)
                    screen.blit(img, (x_pos[i], y))
                y += 35

        back_btn.draw()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if back_btn.clicked(event):
                return "menu"


def settings_screen():
    global settings
    colors = [[0,180,0], [0,120,255], [160,32,240], [255,140,0]]
    color_index = next((i for i, c in enumerate(colors) if c == settings["snake_color"]), 0)

    while True:
        screen.fill(WHITE)
        draw_text_center("SETTINGS", 90, "big")

        grid_btn = Button(280, 170, 240, 45, "Grid: ON" if settings["grid"] else "Grid: OFF")
        color_btn = Button(280, 230, 240, 45, "Change Color")
        save_btn = Button(280, 450, 240, 45, "Save & Back")

        grid_btn.draw()
        color_btn.draw()
        save_btn.draw()

        pygame.draw.rect(screen, tuple(settings["snake_color"]), (360, 305, 80, 35))
        pygame.draw.rect(screen, BLACK, (360, 305, 80, 35), 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if grid_btn.clicked(event):
                settings["grid"] = not settings["grid"]
            if color_btn.clicked(event):
                color_index = (color_index + 1) % len(colors)
                settings["snake_color"] = colors[color_index]
            if save_btn.clicked(event):
                save_settings(settings)
                return "menu"


def game_over_screen(game):
    retry_btn = Button(270, 360, 260, 45, "Retry")
    menu_btn = Button(270, 425, 260, 45, "Main Menu")

    while True:
        screen.fill(WHITE)
        draw_text_center("GAME OVER", 120, "big", RED)
        draw_text_center(f"Final score: {game.score}", 200)
        draw_text_center(f"Level reached: {game.level}", 240)
        draw_text_center(f"Personal best: {game.personal_best}", 280)
        retry_btn.draw()
        menu_btn.draw()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retry_btn.clicked(event):
                return "retry"
            if menu_btn.clicked(event):
                return "menu"


def play_game(username):
    game = Game(username)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and not game.game_over:
                game.handle_key(event.key)

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(game.speed)

        if game.game_over and game.saved:
            action = game_over_screen(game)
            if action == "retry":
                game.reset()
            else:
                return action

setup_database()

username = ""
state = "menu"
running = True

while running:
    if state == "menu":
        state, username = main_menu(username)
    elif state == "play":
        state = play_game(username)
    elif state == "leaderboard":
        state = leaderboard_screen()
    elif state == "settings":
        state = settings_screen()
    elif state == "quit":
        running = False

pygame.quit()