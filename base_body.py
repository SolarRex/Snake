import pygame
from pygame import Surface, transform, font
import argparse
import keyboard  # pip install keyboard
import sys

COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (255, 0, 0)


class BaseBody:
    body_box = None
    # display location, width, and height
    left: int = None
    top: int = None
    width: int = None
    height: int = None

    def __init__(
        self,
        name,
        left: int,
        top: int,
        width: int = 5,
        height: int = 5,
        follows=None,
    ):
        pygame.init()

        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.centerx = left - width / 2
        self.centery = top + height / 2
        self.bottom = top + height
        self.right = left + width
        self.body_box = pygame.Rect(
            self.left,
            self.top,
            self.width,
            self.height,
        )
        self.follows = follows

    # def __del__(self):
    #     try:
    #         self.on_end()
    #     except:
    #         pass
    def set_position(self, left: int, top: int):
        self.left = left
        self.top = top
        self.centerx = left - self.width / 2
        self.centery = top + self.height / 2
        self.bottom = top + self.height
        self.right = left + self.width
        self.body_box.left = left
        self.body_box.top = top

    def get_position(self):
        return self.left, self.top

    def follow(self):
        if self.follows:
            self.set_position(self.follows.left, self.follows.top)

    def draw_body(self, screen: Surface):
        pygame.draw.rect(
            screen,
            COLOUR_WHITE,
            self.body_box,
        )
