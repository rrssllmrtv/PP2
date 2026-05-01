import pygame
import sys
from constants import (
    WIDTH, HEIGHT, FPS,
    WHITE, BLACK, GRAY,
    screen, clock,
    font_small, font_medium, font_big,
)
from persistence import load_leaderboard, add_score, save_settings


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        color = GRAY if self.rect.collidepoint(mouse) else WHITE

        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_img = font_medium.render(self.text, True, BLACK)
        text_rect = text_img.get_rect(center=self.rect.center)
        surface.blit(text_img, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_center_text(text, y, font, color=BLACK):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(WIDTH // 2, y))
    screen.blit(img, rect)


def main_menu():
    play_btn = Button("Play", 150, 230, 200, 55)
    leaderboard_btn = Button("Leaderboard", 150, 300, 200, 55)
    settings_btn = Button("Settings", 150, 370, 200, 55)
    quit_btn = Button("Quit", 150, 440, 200, 55)

    while True:
        screen.fill((210, 230, 255))
        draw_center_text("TSIS3 Racer", 150, font_big)

        play_btn.draw(screen)
        leaderboard_btn.draw(screen)
        settings_btn.draw(screen)
        quit_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_btn.clicked(event):
                return "name"
            if leaderboard_btn.clicked(event):
                return "leaderboard"
            if settings_btn.clicked(event):
                return "settings"
            if quit_btn.clicked(event):
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(FPS)


def name_screen():
    name = ""
    start_btn = Button("Start", 150, 430, 200, 55)
    back_btn = Button("Back", 150, 500, 200, 55)

    while True:
        screen.fill((220, 240, 220))
        draw_center_text("Enter your name", 180, font_medium)

        box = pygame.Rect(100, 260, 300, 55)
        pygame.draw.rect(screen, WHITE, box, border_radius=8)
        pygame.draw.rect(screen, BLACK, box, 2, border_radius=8)

        name_img = font_medium.render(name, True, BLACK)
        screen.blit(name_img, (115, 270))

        start_btn.draw(screen)
        back_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode

            if start_btn.clicked(event) and name.strip():
                return name.strip()
            if back_btn.clicked(event):
                return None

        pygame.display.update()
        clock.tick(FPS)


def settings_screen(settings):
    color_btn = Button("", 120, 200, 260, 50)
    difficulty_btn = Button("", 120, 270, 260, 50)
    back_btn = Button("Back", 150, 480, 200, 55)

    colors = ["original", "blue", "red", "green", "purple"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill((245, 235, 210))
        draw_center_text("Settings", 120, font_big)

        color_btn.text = "Car color: " + settings["car_color"]
        difficulty_btn.text = "Difficulty: " + settings["difficulty"]

        color_btn.draw(screen)
        difficulty_btn.draw(screen)
        back_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if color_btn.clicked(event):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]
                save_settings(settings)

            if difficulty_btn.clicked(event):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                save_settings(settings)

            if back_btn.clicked(event):
                save_settings(settings)
                return "menu"

        pygame.display.update()
        clock.tick(FPS)


def leaderboard_screen():
    back_btn = Button("Back", 150, 610, 200, 55)

    while True:
        screen.fill((230, 230, 250))
        draw_center_text("Top 10 Scores", 70, font_big)

        data = load_leaderboard()
        y = 165
        rank_x, name_x, score_x, dist_x = 60, 120, 260, 370

        screen.blit(font_small.render("Rank", True, BLACK), (rank_x, 125))
        screen.blit(font_small.render("Name", True, BLACK), (name_x, 125))
        screen.blit(font_small.render("Score", True, BLACK), (score_x, 125))
        screen.blit(font_small.render("Distance", True, BLACK), (dist_x, 125))
        pygame.draw.line(screen, BLACK, (55, 155), (445, 155), 2)

        for i, item in enumerate(data[:10]):
            screen.blit(font_small.render(str(i + 1) + ".", True, BLACK), (rank_x, y))
            screen.blit(font_small.render(item["name"][:10], True, BLACK), (name_x, y))
            screen.blit(font_small.render(str(item["score"]), True, BLACK), (score_x, y))
            screen.blit(font_small.render(str(item["distance"]) + "m", True, BLACK), (dist_x, y))
            y += 38

        back_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_btn.clicked(event):
                return "menu"

        pygame.display.update()
        clock.tick(FPS)


def game_over_screen(game):
    add_score(game.username, int(game.score), game.distance, game.coins_collected)

    retry_btn = Button("Retry", 150, 450, 200, 55)
    menu_btn = Button("Main Menu", 150, 520, 200, 55)

    while True:
        screen.fill((255, 220, 220))

        title = "Finish!" if game.finished else "Game Over"
        draw_center_text(title, 120, font_big)

        draw_center_text("Name: " + game.username, 210, font_medium)
        draw_center_text("Score: " + str(int(game.score)), 260, font_medium)
        draw_center_text("Distance: " + str(int(game.distance)) + " m", 310, font_medium)
        draw_center_text("Coins: " + str(game.coins_collected), 360, font_medium)

        retry_btn.draw(screen)
        menu_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if retry_btn.clicked(event):
                return "retry"
            if menu_btn.clicked(event):
                return "menu"

        pygame.display.update()
        clock.tick(FPS)