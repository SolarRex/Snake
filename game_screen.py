import pygame
from pygame import Surface, display, font, transform, mouse
import argparse
import keyboard  # pip install keyboard
import sys
import random
import time

from base_screen import BaseScreen
from base_button import Button
from base_food import BaseFood
from base_body import BaseBody

COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (255, 0, 0)
COLOUR_DARK_GREEN = (0, 100, 0)


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

        self.head = BaseBody(
            "head", self.left + self.width / 2, self.top + self.height / 2
        )
        self.head_direction = 0  # 0 not moving, 1 left, 2 up, 3 right, 4 down
        self.left_eye = BaseBody(
            "left_eye",
            self.head.left + 1,
            self.head.top + 1,
            1,
            1,
            colour=COLOUR_BLACK,
        )
        self.right_eye = BaseBody(
            "right_eye",
            self.head.right - 2,
            self.head.top + 1,
            1,
            1,
            colour=COLOUR_BLACK,
        )
        self.tongue = BaseBody(
            "tongue",
            self.head.left + 2,
            self.head.top - 4,
            3,
            4,
            colour=COLOUR_RED,
        )
        print(self.head.left)
        print(self.tongue.left)
        self.body: list[BaseBody] = [self.head]

        self.food = BaseFood(
            "food",
            random.randint(self.left, self.right - self.head.width),
            random.randint(self.top, self.bottom - self.head.height),
        )

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
        headx = int(self.left + self.width / 2)
        headx = headx - (headx % self.head.width)

        heady = int(self.top + self.height / 2)
        heady = heady - (heady % self.head.height)

        self.head.set_position(headx, heady)
        self.left_eye.set_position(self.head.left + 1, self.head.top + 1)
        self.right_eye.set_position(self.head.right - 2, self.head.top + 1)
        self.tongue.set_position(self.head.left + 1, self.head.top - 4)
        self.tongue_showing = True
        self.last_pause_time = time.time()

        self.head_direction = 0

        self.body = [self.head]

        # for x in range(self.left, self.right):
        #     for y in range(self.top, self.bottom):
        #         self.set_available(x, y, 1, 1, True)

        self.food.set_position(
            random.randint(self.left, self.right - self.head.width),
            random.randint(self.top, self.bottom - self.head.height),
        )

        self.set_available(
            self.left,
            self.top,
            self.width - self.head.width,
            self.height - self.head.height,
            True,
        )

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
        for x in range(left, left + width, self.head.width):
            for y in range(top, top + height, self.head.height):
                self.free_pixel[(x, y)] = available

    def register_on_callback(self, name: str, value: bool) -> bool:
        return value

    def render(self, screen: Surface, callback, mouse_pos=None):
        if self.showing:
            rect_area = pygame.Rect(self.left, self.top, self.width, self.height)
            screen.fill(COLOUR_DARK_GREEN, rect_area)
            self.food.draw_food(screen)

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
                for body in reversed(self.body):
                    body.draw_body(screen)
                    callback(
                        "body_crash",
                        body.name != "head"
                        and self.head.body_box.colliderect(body.body_box),
                    )
                    body.follow()
                self.left_eye.draw_body(screen)
                self.right_eye.draw_body(screen)

                if self.head_direction == 1:
                    self.head.set_position(
                        self.head.left - self.head.width * self.difficulty,
                        self.head.top,
                    )
                    self.left_eye.set_position(self.head.left + 1, self.head.bottom - 2)
                    self.right_eye.set_position(self.head.left + 1, self.head.top + 1)
                    self.tongue.set_dim(4, 3)
                    self.tongue.set_position(self.head.left - 4, self.head.top + 1)
                elif self.head_direction == 2:
                    self.head.set_position(
                        self.head.left,
                        self.head.top - self.head.width * self.difficulty,
                    )
                    self.left_eye.set_position(self.head.left + 1, self.head.top + 1)
                    self.right_eye.set_position(self.head.right - 2, self.head.top + 1)
                    self.tongue.set_dim(3, 4)
                    self.tongue.set_position(self.head.left + 1, self.head.top - 4)
                elif self.head_direction == 3:
                    self.head.set_position(
                        self.head.left + self.head.width * self.difficulty,
                        self.head.top,
                    )
                    self.left_eye.set_position(self.head.right - 2, self.head.top + 1)
                    self.right_eye.set_position(
                        self.head.right - 2, self.head.bottom - 2
                    )
                    self.tongue.set_dim(4, 3)
                    self.tongue.set_position(self.head.right, self.head.top + 1)
                elif self.head_direction == 4:
                    self.head.set_position(
                        self.head.left,
                        self.head.top + self.head.width * self.difficulty,
                    )
                    self.left_eye.set_position(
                        self.head.right - 2, self.head.bottom - 2
                    )
                    self.right_eye.set_position(
                        self.head.left + 1, self.head.bottom - 2
                    )
                    self.tongue.set_dim(3, 4)
                    self.tongue.set_position(self.head.left + 1, self.head.bottom)

                x, y = self.head.get_position()
                callback(
                    "wall_crash",
                    x < self.left
                    or x >= self.right
                    or y < self.top
                    or y >= self.bottom,
                )

                self.set_available(
                    int(x), int(y), int(self.head.width), int(self.head.height), False
                )

                true_keys = [
                    key for key, value in self.free_pixel.items() if value is True
                ]
                if self.head.body_box.colliderect(self.food.food_box):
                    sound = pygame.mixer.Sound(
                        "game_sounds\\freesound_community-arcade-bleep-sound-6071.mp3"
                    )
                    sound.set_volume(0.1)
                    sound.play()

                    choice = random.choice(list(true_keys))
                    self.food.set_position(choice[0], choice[1])
                    self.player_score = self.player_score + 1
                    new_body = BaseBody(
                        f"body_piece_{self.player_score}",
                        -1,
                        -1,
                        follows=self.body[self.player_score - 1],
                    )
                    self.body.append(new_body)

                    print(len(self.body))

            else:
                if self.tongue_showing and time.time() - self.last_pause_time >= 3:
                    self.tongue_showing = False
                    self.last_pause_time = time.time()
                elif (
                    not self.tongue_showing
                    and time.time() - self.last_pause_time >= 0.5
                ):
                    self.last_pause_time = time.time()
                    self.tongue_showing = True

                screen.blit(self.paused_text, self.paused_text_rect)

                for body in self.body:
                    body.draw_body(screen)
                self.left_eye.draw_body(screen)
                self.right_eye.draw_body(screen)
                if self.tongue_showing:
                    self.tongue.draw_body(screen)
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
