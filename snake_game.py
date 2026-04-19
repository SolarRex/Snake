import pygame
from pygame import Surface, display, font, transform, mouse
import argparse
import sys

# from pynput.keyboard import Key, Listener
from pynput import keyboard, mouse
import time
import threading
import tkinter as tk
import queue

from base_screen import BaseScreen
from base_button import Button
from title_screen import TitleScreen
from game_screen import GameScreen
from score_screen import ScoreScreen
from end_screen import EndScreen


COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (255, 0, 0)
DEFAULT_WIDTH = "500"
DEFAULT_HEIGHT = "500"
TRUE_SET = {"true", "t", "y", "yes", "1"}
FALSE_SET = {"false", "f", "n", "no", "0"}
FPS = 30  # unsure why, but this is half what the actual fps is, e.g. 30 -> 60fps,


class Snake:
    paused = False
    player_score = 0

    top_fps = 0
    bottom_fps = 10000
    ave = 0.0
    count = 0

    def __init__(self, width, height, fullscreen, xfullscreen, player_name):
        if fullscreen in TRUE_SET:
            self.width, self.height = self.get_screen_resolution()
        else:
            self.width = width
            self.height = height

        self.title_screen: BaseScreen = TitleScreen(
            "title_screen", width=self.width, height=self.height
        )
        self.game_screen: BaseScreen = GameScreen(
            "game_screen",
            top=int(self.height / 5),
            width=self.width,
            height=int(self.height * 4 / 5),
        )
        self.score_screen: BaseScreen = ScoreScreen(
            "score_screen", width=self.width, height=int(self.height / 5)
        )
        self.end_screen: BaseScreen = EndScreen(
            "end_screen", width=self.width, height=self.height, player_name=player_name
        )
        if xfullscreen in TRUE_SET:
            self.display = pygame.display.set_mode(
                (self.width, self.height), pygame.FULLSCREEN
            )
        else:
            self.display = pygame.display.set_mode((self.width, self.height))
        self.running = True
        self.bot_difficulty = 5

        self.clock = pygame.time.Clock()
        self.previous_time_tick = time.time()
        self.callback_queue = queue.Queue()

        pygame.mixer.init()
        pygame.mixer.music.load(
            "game_sounds\sonican-background-music-new-age-nature-465069.mp3"
        )
        pygame.mixer.music.set_volume(0.1)

    def on_callback(self, callable):
        threading.Thread(target=callable, daemon=True).start()

    def on_start(self):
        pygame.mixer.music.play(-1)
        self.running = True
        self.title_screen.on_start()
        self.player_score = 0
        self.game_screen.player_score = self.player_score

    def on_restart(self):
        self.running = False
        self.title_screen.on_end()
        self.game_screen.on_end()
        self.score_screen.on_end()
        self.end_screen.on_end()
        print("Restarting")
        time.sleep(2)
        self.on_start()

    def on_end(self):
        self.running = False
        self.title_screen.on_end()
        self.game_screen.on_end()
        self.score_screen.on_end()
        self.end_screen.on_end()
        print("exiting")
        print("------------------------------")
        print(f"Top FPS was {self.top_fps}")
        print(f"Bottom FPS was {self.bottom_fps}")
        print(f"The average FPS was {self.ave/self.count}")
        pygame.quit()

    def toggle_pause(self, *kwargs) -> bool:
        self.paused = not self.paused
        self.game_screen.toggle_pause()
        if self.paused:
            print("paused")
        else:
            print("unpaused")

        return self.paused

    def get_screen_resolution(self):
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return width, height
        except Exception as e:
            print(
                f"Error retrieving resolution: {e}. Setting to default resolution ({DEFAULT_WIDTH}, {DEFAULT_HEIGHT})"
            )
            return None, None

    def register_on_callback(self, name: str, value: bool) -> bool:
        self.callback_queue.put(value)
        return value

    def pop_callback(self) -> bool:
        if self.callback_queue.empty:
            LookupError("nothing in queue")
        return self.callback_queue.get(block=False)


def main():
    parser = argparse.ArgumentParser(description="Start the game with settings")
    parser.add_argument(
        "--speed",
        type=str,
        default="1",
        help="The speed which ranges from 1 to 10, out of this range will set to either 1 or 10.",
    )
    parser.add_argument(
        "--width",
        type=str,
        default=DEFAULT_WIDTH,
        help="Sets the width of the screen.",
    )
    parser.add_argument(
        "--height",
        type=str,
        default=DEFAULT_HEIGHT,
        help="Sets the height of the screen.",
    )
    parser.add_argument(
        "--fullscreen",
        type=str,
        default="False",
        help="Sets to the monitors resolution.",
    )
    parser.add_argument(
        "--exclusive_fullscreen",
        type=str,
        default="False",
        help="Sets to exclusive fullscreen.",
    )
    parser.add_argument(
        "--player_name",
        type=str,
        default="NO NAME",
        help="Sets the name of the player.",
    )

    args = parser.parse_args()
    args_info = {
        "width": int(args.width),
        "height": int(args.height),
        "fullscreen": args.fullscreen.lower(),
        "xfullscreen": args.exclusive_fullscreen.lower(),
        "player_name": args.player_name,
    }

    snake_game = Snake(
        width=args_info["width"],
        height=args_info["height"],
        fullscreen=args_info["fullscreen"],
        xfullscreen=args_info["xfullscreen"],
        player_name=args_info["player_name"],
    )

    snake_game.on_start()

    snake_game.count = 0
    snake_game.ave = 0

    try:
        while snake_game.running:
            # -------------------------------------------------------
            snake_game.clock.tick(0)
            fps = snake_game.clock.get_fps()

            if time.time() - snake_game.previous_time_tick >= 1.0:
                snake_game.previous_time_tick = time.time()
                snake_game.score_screen.fps = fps
                print(fps)

            snake_game.top_fps = max(fps, snake_game.top_fps)
            snake_game.bottom_fps = min(fps, snake_game.bottom_fps)
            snake_game.ave = snake_game.ave + fps
            snake_game.count = snake_game.count + 1

            # -------------------------------------------------------
            button_free = True
            snake_game.display.fill(COLOUR_BLACK)

            if snake_game.end_screen.showing:
                snake_game.end_screen.render(snake_game.display)

            else:
                mouse_pos = pygame.mouse.get_pos()
                snake_game.title_screen.render(snake_game.display, mouse_pos)
                snake_game.game_screen.render(
                    snake_game.display,
                    snake_game.register_on_callback,
                    mouse_pos,
                )

                if snake_game.game_screen.showing and not snake_game.game_screen.paused:
                    while not snake_game.callback_queue.empty():
                        if snake_game.pop_callback():
                            # print("crashed")
                            snake_game.title_screen.on_end()
                            snake_game.game_screen.on_end()
                            snake_game.score_screen.on_end()
                            snake_game.end_screen.set_score(snake_game.player_score)
                            snake_game.end_screen.on_start()

                snake_game.player_score = snake_game.game_screen.player_score
                snake_game.score_screen.player_score = snake_game.player_score

                snake_game.score_screen.render(snake_game.display)

            # pygame.QUIT event means the user clicked X to close your window
            # keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    snake_game.on_end()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        snake_game.on_end()
                        return
                    if event.key == pygame.K_p:
                        if snake_game.game_screen.showing:
                            snake_game.toggle_pause()
                    if event.key == pygame.K_r and not snake_game.title_screen.showing:
                        snake_game.on_restart()
                    if button_free:
                        if (
                            snake_game.game_screen.head_direction != 3
                            and event.key == pygame.K_LEFT
                        ):
                            snake_game.game_screen.head_direction = 1
                        elif (
                            snake_game.game_screen.head_direction != 4
                            and event.key == pygame.K_UP
                        ):
                            snake_game.game_screen.head_direction = 2
                        elif (
                            snake_game.game_screen.head_direction != 1
                            and event.key == pygame.K_RIGHT
                        ):
                            snake_game.game_screen.head_direction = 3
                        elif (
                            snake_game.game_screen.head_direction != 2
                            and event.key == pygame.K_DOWN
                        ):
                            snake_game.game_screen.head_direction = 4
                        button_free = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    try:

                        snake_game.title_screen

                        if snake_game.title_screen.on_button_click() == "start":

                            snake_game.title_screen.on_end()
                            snake_game.game_screen.on_start()

                            snake_game.score_screen.on_start()

                        elif snake_game.title_screen.on_button_click() == "exit":
                            snake_game.on_end()
                    except:
                        pass

                    try:
                        snake_game.game_screen
                        if snake_game.game_screen.on_button_click() == "pause":
                            snake_game.toggle_pause()
                        if snake_game.game_screen.on_button_click() == "exit":
                            snake_game.on_end()
                    except:
                        pass
            display.flip()

            snake_game.clock.tick(FPS)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        if snake_game.running:
            snake_game.on_end()
            print("\nProgram interrupted by user.")


if __name__ == "__main__":
    main()
