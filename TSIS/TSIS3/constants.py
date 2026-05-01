import pygame

pygame.init()

WIDTH = 500
HEIGHT = 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
RED = (220, 40, 40)
GREEN = (40, 180, 80)
BLUE = (50, 120, 220)
YELLOW = (230, 200, 40)
ORANGE = (230, 130, 40)
PURPLE = (150, 70, 220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Verdana", 18)
font_medium = pygame.font.SysFont("Verdana", 26)
font_big = pygame.font.SysFont("Verdana", 48)

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

LANES = [115, 195, 275, 355]
ROAD_LEFT = 75
ROAD_RIGHT = 425
FINISH_DISTANCE = 3000