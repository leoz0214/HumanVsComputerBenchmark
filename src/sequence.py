"""
Sequence test. Who has better sequential memory, you or your computer?
This test will find out!
For the computer, headless is overpowered, with window is a bit bad!
"""
import random
import time
from collections import namedtuple
from timeit import default_timer as timer

import lxml
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

import main
from utils import DATA_FOLDER, get_log_function, log_date_time


# Seconds to sleep before starting a level.
INITIAL_DELAY = 1.25
# Fixed optimal delay in seconds between scanning
# the squares as they appear.
DELAY_BETWEEN_SQUARES = 0.5
LOG = DATA_FOLDER / "sequence.txt"
# Random chance of failure to avoid potentially going on forever.
FAILURE_RATE = 0.03


SequenceResult = namedtuple(
    "SequenceResult",
    ("final_sequence", "score", "longest_sub_sequence")
)
log = get_log_function(LOG)


def longest_duplicate_subarray(array: list[int]) -> list[int]:
    """
    Returns the longest sub-array that appears more than once in the array.
    If multiple sub-arrays have the same maximum length, returns the first.
    If there are no duplicates whatsoever, return an empty list.
    """
    # Converts to tuple right away for hashing purposes.
    array = tuple(array)
    # Tries lengths from largest to smallest.
    for length in range(len(array) - 1, 0, -1):
        # Stores seen subarrays for the given length.
        seen = set()
        for start_index in range(len(array) - length + 1):
            sub_array = array[start_index:start_index+length]
            if sub_array in seen:
                return list(sub_array)
            seen.add(sub_array)
    return []


def get_sequence_result(final_sequence: list[int]) -> SequenceResult:
    """Generates the sequence result."""
    score = len(final_sequence)
    longest_sub_sequence = longest_duplicate_subarray(final_sequence)
    return SequenceResult(final_sequence, score, longest_sub_sequence)


def sequence(driver: "main.ComputerBenchmark") -> SequenceResult:
    """Performs the sequence test and returns the result."""
    log_date_time(log, "Sequence memory test started at {} UTC.")
    driver.get_test("sequence")
    driver.click_start()
    level = 1
    # Track previous sequence to output it as the final result
    # (the last successful sequence).
    previous_sequence = []
    while True:
        sequence = []
        time.sleep(INITIAL_DELAY)
        for _ in range(level):
            start = timer()
            try:
                soup = BeautifulSoup(driver.page_source, "lxml")
                squares = soup.find(class_="squares")
                for i, square in enumerate(squares.find_all(class_="square")):
                    if "active" in square["class"]:
                        sequence.append(i)
                        stop = timer()
                        # Ensures 0.5s pretty much exactly between checking
                        # each square appearing in the sequence. This includes
                        # the processing time beforehand, to avoid a delay
                        # of greater than 0.5s overall, since the BeautifulSoup
                        # processing takes a few milliseconds, which matters...
                        time.sleep(DELAY_BETWEEN_SQUARES - (stop - start))
                        break
                else:
                    # Missed a square - in big trouble - surrender!
                    log("Missed a square - game over.")
                    return get_sequence_result(previous_sequence)
            except Exception:
                print("An error has occurred while performing the test.")
                return get_sequence_result(previous_sequence)
        log(f"Level {level}: {sequence}")
        try:
            for i in sequence:
                driver.find_elements(By.CLASS_NAME, "square")[i].click()
        except Exception:
            log("Error while clicking!")
            return get_sequence_result(previous_sequence)
        level += 1
        previous_sequence = sequence
        if random.random() < FAILURE_RATE:
            log("Random failure activated to avoid going on forever.")
            return get_sequence_result(previous_sequence)
