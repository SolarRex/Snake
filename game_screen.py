import pygame
from pygame import Surface, display, font, transform, mouse
import argparse
import keyboard  # pip install keyboard
import sys
import random

from base_screen import BaseScreen
from base_button import Button
from base_food import BaseFood
from base_body import BaseBody

COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (255, 0, 0)


class GameScreen(BaseScreen):
    showing = False
    paused = False

    # display location, width, and height
    left: int = None
    top: int = None
    width: int = None
    height: int = None
    bottom: int = None
    right: int = None
    player_score = 0

    def __init__(
        self,
        name,
        left=0,
        top=0,
        width=320,
        height=320,
        buttons: list = None,
        player_score: int = 0,
        difficulty: int = 1,
    ):
        super().__init__(name)

        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.bottom = top + height
        self.right = left + width
        self.player_score = player_score
        self.difficulty = difficulty

        self.screen_multipliery = self.height / 400
        self.screen_multiplierx = self.width / 500

        self.font = font.SysFont("arial", 50)
        self.small_font = font.SysFont("arial", 25)

        self.food = BaseFood(
            "food",
            random.uniform(self.left, self.right),
            random.uniform(self.top, self.bottom),
        )

        self.head = BaseBody(
            "head", self.left + self.width / 2, self.top + self.height / 2
        )
        self.head_direction = 0  # 0 not moving, 1 left, 2 up, 3 right, 4 down

        self.body: list[BaseBody] = [self.head]

        self.paused_text = self.font.render(
            f"PAUSED",
            True,
            COLOUR_WHITE,
        )
        self.paused_text_rect = self.paused_text.get_rect(
            center=(self.left + self.width / 2, self.top + self.height / 2 - 50)
        )

        self.pause_button = Button(
            "pause_button",
            "Unpause",
            COLOUR_BLACK,
            25,
            (self.width / 2 - 50, self.height / 2 + 50),
            COLOUR_GREEN,
            COLOUR_RED,
            self.left,
            self.top,
        )

        self.exit_button = Button(
            "exit_button",
            "Exit",
            COLOUR_BLACK,
            25,
            (self.width / 2 + 50, self.height / 2 + 50),
            COLOUR_GREEN,
            COLOUR_RED,
            self.left,
            self.top,
        )

        self.free_pixel: dict[tuple[int, int], bool] = {}

    # def __del__(self):
    #     try:
    #         self.on_end()
    #     except:
    #         pass

    def on_start(self) -> bool:
        self.showing = True
        self.paused = False

        self.player_score = 0

        self.head.set_position(self.left + self.width / 2, self.top + self.height / 2)

        self.head_direction = 0

        self.body = [self.head]

        for x in range(self.left, self.width):
            for y in range(self.top, self.height):
                self.set_available(x, y, 1, 1, True)

        self.set_available(
            self.head.left, self.head.top, self.head.width, self.head.height
        )

        return True

    def on_end(self) -> bool:
        self.showing = False
        print("Exiting Game")
        return False

    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        if self.paused:
            self.head_hold_dir = self.head_direction
            self.head_direction = 0
        else:
            self.head_direction = self.head_hold_dir

        return self.paused

    def set_available(
        self, left: int, top: int, width: int, height: int, available: bool = False
    ):
        for x in range(left, left + width):
            for y in range(top, top + height):
                self.free_pixel[(x, y)] = available

    def render(self, screen: Surface, mouse_pos=None):
        if self.showing:
            self.food.draw_food(screen)
            for body in self.body:
                body.follow()
                body.draw_body(screen)

            if not self.paused:  # 0 not moving, 1 left, 2 up, 3 right, 4 down
                last_body_piece = self.body[-1]
                x, y = last_body_piece.get_position()
                self.set_available(
                    int(x),
                    int(y),
                    int(last_body_piece.width),
                    int(last_body_piece.height),
                    True,
                )
                if self.head_direction == 1:
                    self.head.set_position(
                        self.head.left - self.head.width * self.difficulty,
                        self.head.top,
                    )
                elif self.head_direction == 2:
                    self.head.set_position(
                        self.head.left,
                        self.head.top - self.head.width * self.difficulty,
                    )
                elif self.head_direction == 3:
                    self.head.set_position(
                        self.head.left + self.head.width * self.difficulty,
                        self.head.top,
                    )
                elif self.head_direction == 4:
                    self.head.set_position(
                        self.head.left,
                        self.head.top + self.head.width * self.difficulty,
                    )
                x, y = self.head.get_position()
                self.set_available(
                    int(x), int(y), int(self.head.width), int(self.head.height), False
                )

                true_keys = [
                    key for key, value in self.free_pixel.items() if value is True
                ]
                if self.head.body_box.colliderect(self.food.food_box):
                    choice = random.choice(list(true_keys))
                    self.food.set_position(choice[0], choice[1])
                    self.player_score = self.player_score + 1
                    new_body = BaseBody(
                        f"body_piece_{self.player_score - 1}",
                        self.body[self.player_score - 1].left,
                        self.body[self.player_score - 1].top,
                        follows=self.body[self.player_score - 1],
                    )
                    self.body.append(new_body)

            else:
                screen.blit(self.paused_text, self.paused_text_rect)

                # button

                self.pause_button.is_hovering(mouse_pos)
                self.pause_button.draw_button(screen, 8)

                self.exit_button.is_hovering(mouse_pos)
                self.exit_button.draw_button(screen, 8)

    def on_button_click(self) -> str:
        # print("Button was clicked!")
        if self.paused:
            try:
                self.pause_button
                if self.pause_button.hovered_over:
                    return "pause"
            except:
                return "didn't press"
            try:
                self.exit_button
                if self.exit_button.hovered_over:
                    return "exit"
            except:
                return "didn't press"
