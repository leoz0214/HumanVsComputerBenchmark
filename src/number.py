"""
The average human can remember 7 numbers.
Can you do more? Hopefully you can...
The average computer can remember like 8 billion numbers.
Can you do more?! Hopefully you cannot...
"""
import random
from collections import namedtuple

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import main
from utils import DATA_FOLDER, get_log_function, log_date_time


# A small chance of failure to avoid going on forever.
FAILURE_RATE = 0.05
LOG = DATA_FOLDER / "number.txt"

NumberResult = namedtuple(
    "NumberResult",
    ("score", "numbers", "total_digits", "digit_breakdown")
)
log = get_log_function(LOG)


def get_number_result(numbers: list[int]) -> NumberResult:
    """Generates the results for the number memory test."""
    score = len(numbers)
    total_digits = (score * (score + 1)) // 2
    digit_breakdown = {n: 0 for n in range(10)}
    for number in numbers:
        for digit in str(number):
            digit_breakdown[int(digit)] += 1
    return NumberResult(score, numbers, total_digits, digit_breakdown)


def number(driver: "main.ComputerBenchmark") -> NumberResult:
    """Performs the number memory test and returns the result."""
    log_date_time(log, "Number memory test started at {} UTC.")
    driver.get_test("number-memory")
    driver.click_start()
    numbers = []
    while True:
        try:
            number_element = driver.wait((By.CLASS_NAME, "big-number "), 5)
            number = int(number_element.text)
            # Wait for entry to appear, longer as the number length increases.
            entry = driver.wait((By.TAG_NAME, "input"), len(numbers) + 10)
            # Inputs the number, and presses ENTER twice.
            # The first ENTER submits the number.
            # The second ENTER proceeds to the next number.
            entry.send_keys(f"{number}{Keys.ENTER * 2}")
            if "Save score" in driver.page_source:
                # Number was somehow incorrectly input - game over.
                solution = driver.find_element(By.CLASS_NAME, "actual-answer")
                actual_answer = int(
                    solution.find_element(By.CLASS_NAME, "number").text)
                log(
                    f"Game over - {number} was input, "
                    f"{actual_answer} is the correct answer.")
                break
        except Exception:
            log("An error has occurred with the test.")
            break
        numbers.append(number)
        log(f"{len(numbers)}. {number}")
        if random.random() < FAILURE_RATE:
            log("Failing now to avoid going on forever.")
            break
    return get_number_result(numbers)
