import pygame
from pygame import Surface, display, font, transform, mouse

COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (255, 0, 0)


class BaseFood:
    food_box = None

    def __init__(
        self,
        name,
        left: int,
        top: int,
        width: int = 5,
        height: int = 5,
    ):
        pygame.init()

        self.name = name
        self.left = left
        self.top = top
        self.right = left + width
        self.bottom = top + height
        self.width = width
        self.height = height
        self.centerx = left - width / 2
        self.centery = top + height / 2
        self.food_box = pygame.Rect(
            self.left,
            self.top,
            self.width,
            self.height,
        )

    def set_position(self, left, top):
        self.left = left
        self.centerx = self.left + self.width / 2
        self.right = self.left + self.width

        self.top = top
        self.centery = self.centery + self.height / 2
        self.bottom = self.top + self.height

        self.food_box.left = self.left
        self.food_box.top = self.top

    def draw_food(self, screen: Surface):
        pygame.draw.rect(
            screen,
            COLOUR_RED,
            self.food_box,
        )
