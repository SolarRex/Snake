import pygame
from pygame import Surface, transform, font
import argparse
import keyboard  # pip install keyboard
import sys
import os

from base_screen import BaseScreen

COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (255, 0, 0)
MAX_ENTRIES = 10  # Keep only top 10 scores


class EndScreen(BaseScreen):
    showing = False
    paused = False

    # display location, width, and height
    left: int = None
    top: int = None
    width: int = None
    height: int = None
    score: int = None

    def __init__(
        self,
        name,
        left=0,
        top=0,
        width=320,
        height=320,
        buttons: list = None,
        player_name: str = "NO NAME",
    ):
        super().__init__(name)

        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.font = font.SysFont("arial", 60)
        self.small_font = font.SysFont("arial", 25)
        self.score = 0
        self.player_name = player_name

    def on_start(self) -> bool:
        self.showing = True
        highscore = self.read_first_line("scores.txt")
        if not highscore:
            text = f"New Highscore!"
        elif self.score > int(highscore.split(",")[1]):
            text = f"New Highscore!"
        else:
            text = f"Your Score"
        self.text = self.font.render(
            text,
            True,
            COLOUR_WHITE,
        )
        self.text_rect = self.text.get_rect(
            center=(
                self.left + self.width / 2,
                self.top + self.height / 2 - (self.font.size(text)[1] * 0.55),
            )
        )
        text = f"{self.score}"
        self.score_text = self.font.render(
            text,
            True,
            COLOUR_WHITE,
        )
        self.score_text_rect = self.score_text.get_rect(
            center=(
                self.left + self.width / 2,
                self.top + self.height / 2 + (self.font.size(text)[1] * 0.55),
            )
        )
        self.update_highscores("scores.txt", self.player_name, self.score)
        return True

    def on_end(self) -> bool:
        self.showing = False
        return False

    def toggle_pause(self) -> bool:
        self.pause = not self.pause
        return self.pause

    def render(self, screen: Surface):
        if self.showing:
            screen.blit(self.text, self.text_rect)
            screen.blit(self.score_text, self.score_text_rect)

    def set_score(self, score: int = 0):
        self.score = score

    def draw_button(
        self,
        button_box,
        button_text,
        button_rect,
        screen: Surface,
        hover=False,
    ):
        raise NotImplementedError()

    def on_button_click():
        raise NotImplementedError()

    def read_highscores(self, filename):
        """Read highscores from file and return as a list of (name, score) tuples."""
        scores = []
        if not os.path.exists(filename):
            return scores

        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        name, score_str = parts
                        try:
                            score = int(score_str)
                            scores.append((name, score))
                        except ValueError:
                            pass  # Ignore invalid score lines
        except OSError as e:
            print(f"Error reading file: {e}")
        return scores

    def write_highscores(self, filename, scores):
        """Write highscores to file in descending order."""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for name, score in scores:
                    file.write(f"{name},{score}\n")
        except OSError as e:
            print(f"Error writing file: {e}")

    def update_highscores(self, filename, player_name, player_score):
        """Add a new score and save the updated highscore list."""
        scores = self.read_highscores(filename)
        scores.append((player_name, player_score))

        # Sort by score (descending), then by name (optional)
        scores.sort(key=lambda x: x[1], reverse=True)

        # Keep only top N scores
        scores = scores[:MAX_ENTRIES]

        self.write_highscores(filename, scores)

    def read_first_line(self, file_path):
        """
        Reads and returns the first line of a text file.
        Strips the newline character at the end.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                first_line = file.readline()
                return first_line.strip() if first_line else None
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except PermissionError:
            print(f"Error: Permission denied for file '{file_path}'.")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
