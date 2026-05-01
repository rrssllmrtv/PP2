import pygame
import sys
from constants import FPS, clock
from persistence import load_settings
from racer import Game
from ui import main_menu, name_screen, settings_screen, leaderboard_screen, game_over_screen


def play_game(username, settings):
    game = Game(username, settings)

    while not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        game.update()
        game.draw()

        pygame.display.update()
        clock.tick(FPS)

    return game_over_screen(game)


settings = load_settings()
state = "menu"
username = ""

while True:
    if state == "menu":
        state = main_menu()

    elif state == "name":
        entered_name = name_screen()

        if entered_name is None:
            state = "menu"
        else:
            username = entered_name
            state = "game"

    elif state == "game":
        result = play_game(username, settings)

        if result == "retry":
            state = "game"
        else:
            state = "menu"

    elif state == "leaderboard":
        state = leaderboard_screen()

    elif state == "settings":
        state = settings_screen(settings)