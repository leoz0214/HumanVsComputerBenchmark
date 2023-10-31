"""
Who has better visual memory, you or your computer?
If you have functioning eyes, you have a chance. That's all I will say.
"""
import random
import time
from collections import namedtuple

import lxml
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import main
from utils import DATA_FOLDER, get_log_function, log_date_time, get_islands


# How many squares on level 1.
STARTING_SQUARES = 3
# Number of lives provided by the test.
LIVES = 3
# Maximum grey squares allowed before a life is lost.
MAX_GREY = 3
# Random chance to automatically end, to avoid going on forever.
FAILURE_RATE = 0.03
LOG = DATA_FOLDER / "visual.txt"


VisualResult = namedtuple(
    "VisualResult",
    ("score", "total_squares", "boards")
)
# Stores board grid and the island sizes.
Board = namedtuple("Board", ("grid", "islands"))
log = get_log_function(LOG)


class GreySquareException(Exception):
    """Maximum grey squares reached."""
    pass


def get_visual_result(level_lost: int, boards: list[Board]) -> VisualResult:
    """Generates and returns the visual memory result."""
    score = level_lost - 1
    if not score:
        return VisualResult(0, 0, [])
    total_squares = ((score + 2) * (score + 3)) // 2 - 3
    return VisualResult(score, total_squares, boards)


def visual(driver: "main.ComputerBenchmark") -> VisualResult:
    """Performs the visual memory test and returns the result."""
    log_date_time(log, "Visual memory test started at {} UTC.")
    driver.get_test("memory")
    # Move down the page a bit to minimise ad intrusivity.
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.DOWN)
    driver.click_start()
    boards = []
    lives = LIVES
    level = 1
    while True:
        log(f"Level {level}")
        time.sleep(1.5)
        try:
            soup = BeautifulSoup(driver.page_source, "lxml")
            grid = soup.find(class_="eut2yre0")
            # Identifies the ACTIVE squares, which are the ones to be
            # clicked. Converts True to 1 and False to 0 for convenient output.
            board = [
                [int("active" in square["class"]) for square in row.find_all()]
                for row in grid.find_all("div", recursive=False)]
        except Exception:
            log("An error occurred while trying to identify the pattern.")
            break
        # The number of active squares is expected to be 2 more
        # than the current level number. If a single square is missing,
        # then guesswork is needed, otherwise a life will be lost.
        active_squares = sum(map(sum, board))
        missing_squares = (level + STARTING_SQUARES - 1) - active_squares
        if missing_squares:
            log("Missing squares, will need to try and guess correctly.")
        time.sleep(1)
        try:
            grid = driver.find_element(By.CLASS_NAME, "eut2yre0")
            grid_rows = [
                div for div in grid.find_elements(By.TAG_NAME, "div")
                if not div.get_attribute("class")]
            grey = 0
            for i, (grid_row, row) in enumerate(zip(grid_rows, board)):
                for j, (grid_square, square) in enumerate(
                    zip(grid_row.find_elements(By.TAG_NAME, "div"), row)
                ):
                    if square:
                        # Square has been detected to be included.
                        # Simply click it.
                        grid_square.click()
                    elif missing_squares:
                        # Might as well guess and try this square!
                        grid_square.click()
                        if "error" in grid_square.get_attribute("class"):
                            # No luck - encountered a grey square.
                            grey += 1
                            if grey == MAX_GREY:
                                raise GreySquareException
                            continue
                        # Active found by luck, set the square to active.
                        board[i][j] = 1
                        missing_squares -= 1
        except GreySquareException:
            log("Maximum failed guesses reached.")
            lives -= 1
            if not lives:
                log("Out of lives.")
                break
            continue
        except Exception:
            log("An error occurred while trying to click the squares.")
            break
        islands = get_islands(board)
        log(f"{len(board)}x{len(board)}")
        for row in board:
            log(row)
        log(f"Islands: {islands}")
        boards.append(Board(board, islands))
        level += 1
        if random.random() < FAILURE_RATE:
            log("Random failure activated to avoid going on forever.")
            break
        time.sleep(1)
    return get_visual_result(level, boards)
