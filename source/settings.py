import os
from configparser import ConfigParser
from ctypes import windll
from pathlib import Path

import pygame

pygame.font.init()
windll.user32.SetProcessDPIAware()

vec = pygame.math.Vector2

FPS = 60


class PATH:
    ROOT = Path(__file__).parents[1]
    SOURCE = os.path.join(ROOT, "source")
    DATA = os.path.join(ROOT, "data")
    FONT = os.path.join(ROOT, "data", "font.ttf")
    CONFIG = os.path.join(ROOT, "data", "config.ini")


parser = ConfigParser()
parser.read(PATH.CONFIG)


class SETTINGS:
    LENGTH = 3
    SPEED = parser.getfloat("SETTINGS", "period")
    ACCELERATION = parser.getfloat("SETTINGS", "acceleration")
    WIDTH, HEIGHT = [int(d.strip()) for d in parser.get("SETTINGS", "map size").split(",")]
    TILE = parser.getint("SETTINGS", "tile size")
    GAP = TILE // 16
    WALLS = parser.getint("SETTINGS", "walls")


class COLORS:
    BACKGROUND = (50, 200, 100)
    BODY = (0, 150, 0)
    PATTERN = (0, 80, 0)
    APPLE = (200, 0, 0)
    HEAD = (0, 100, 0)
    TEXT_1 = (0, 180, 0)
    TEXT_2 = (200, 100, 0)
    EXIT_BUTTON = (200, 20, 20)
    SETTINGS_BUTTON = (0, 150, 0)
    BUTTON = (0, 120, 0)


class DIRECTION:
    UP = vec(0, -1)
    DOWN = vec(0, 1)
    LEFT = vec(-1, 0)
    RIGHT = vec(1, 0)


class RECT:
    WINDOW = (SETTINGS.WIDTH * SETTINGS.TILE, (SETTINGS.HEIGHT + 1) * SETTINGS.TILE)
    CENTER = (int(SETTINGS.WIDTH * SETTINGS.TILE / 2), int(SETTINGS.HEIGHT * SETTINGS.TILE / 2))
    HEAD = (0, 0, SETTINGS.WIDTH * SETTINGS.TILE, SETTINGS.TILE)
    HUD = (0, (SETTINGS.HEIGHT + 1) * SETTINGS.TILE, SETTINGS.WIDTH * SETTINGS.TILE, SETTINGS.TILE)
    BODY = (SETTINGS.GAP, SETTINGS.GAP, SETTINGS.TILE - SETTINGS.GAP * 2, SETTINGS.TILE - SETTINGS.GAP * 2)
    APPLE = (SETTINGS.GAP * 2, SETTINGS.GAP * 2, SETTINGS.TILE - SETTINGS.GAP * 4, SETTINGS.TILE - SETTINGS.GAP * 4)
    PATTERN = (SETTINGS.GAP * 5, SETTINGS.GAP * 5, SETTINGS.TILE - SETTINGS.GAP * 10, SETTINGS.TILE - SETTINGS.GAP * 10)
    LEFT_EYE = (SETTINGS.GAP * 4, SETTINGS.GAP * 4, SETTINGS.GAP * 5, SETTINGS.GAP * 5)
    RIGHT_EYE = (SETTINGS.TILE - SETTINGS.GAP * 9, SETTINGS.GAP * 4, SETTINGS.GAP * 5, SETTINGS.GAP * 5)
    SCORE_1 = (SETTINGS.GAP * 4, 0.5 * SETTINGS.TILE)
    SCORE_2 = (SETTINGS.TILE * 2.5, 0.5 * SETTINGS.TILE)
    EXIT_BUTTON = ((SETTINGS.WIDTH - 1) * SETTINGS.TILE, 0, SETTINGS.TILE, SETTINGS.TILE)
    SETTINGS_BUTTON = ((SETTINGS.WIDTH - 2) * SETTINGS.TILE, 0, SETTINGS.TILE, SETTINGS.TILE)
    KEY_TOOLTIP = (SETTINGS.WIDTH * SETTINGS.TILE, SETTINGS.TILE)


class LABEL:
    SCORE = "Score: "
    GAME_OVER = "GAME OVER ", '[press "r" to restart]'
    PAUSED = "PAUSED ", '[press "p" to continue]'
    KEY_TOOLTIP = "Key configuration"


KEYS = {key: pygame.key.key_code(parser.get("KEYS", key)) for key in parser["KEYS"]}
FONT = [
    pygame.font.Font(PATH.FONT, int(SETTINGS.TILE * 0.8)),
    pygame.font.Font(PATH.FONT, int(SETTINGS.TILE * 1.5))
]
