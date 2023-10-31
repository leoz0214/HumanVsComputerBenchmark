"""
Reaction speed test. Who is faster, you or your computer?
This will mostly depend on what type of crazy video ads are
loaded onto the screen! But most likely the computer...
"""
import statistics
from collections import namedtuple

from selenium.webdriver.common.by import By

import main
from utils import DATA_FOLDER, get_log_function, log_date_time


ROUNDS = 5
LOG = DATA_FOLDER / "reaction_time.txt"


ReactionTimeResult = namedtuple(
    "ReactionTimeResult",
    ("times", "mean", "geometric_mean", "median", "best")
)
log = get_log_function(LOG)


def get_reaction_time_result(times: list[int]) -> ReactionTimeResult:
    """Provides various basic, relevant stats on the times."""
    if not times:
        # Not a single result - something went wrong for this to happen...
        return ReactionTimeResult([], None, None, None, None)
    # Utilise various statistical functions to provide results insight.
    mean = statistics.mean(times)
    geometric_mean = statistics.geometric_mean(times)
    median = statistics.median(times)
    best = min(times)
    return ReactionTimeResult(times, mean, geometric_mean, median, best)


def reaction_time(driver: "main.ComputerBenchmark") -> ReactionTimeResult:
    """Performs the reaction time test and returns the result."""
    log_date_time(log, "Reaction time test started at {} UTC.")
    driver.get_test("reactiontime")
    times = []
    for round_ in range(ROUNDS):
        try:
            driver.find_element(By.TAG_NAME, "h1").click()
            click_element = driver.wait(
                (By.XPATH, "//div[text()='Click!']"), 20)
            click_element.click()
            ms = int(driver.wait((By.TAG_NAME, "h1")).text.removesuffix("ms"))
        except Exception:
            log("An error has occurred while performing the test.")
            break
        if round_ == ROUNDS - 1:
            # Cannot directly access 5th, after the last attempt, the
            # average of 5 is shown. But can approximate the actual 5th.
            # [a, b, c, d, e], mean = f, e = f * 5 - (a + b + c + d)
            ms = ms * ROUNDS - sum(times)
        log(f"Attempt {round_ + 1}: {ms}ms")
        times.append(ms)
    return get_reaction_time_result(times)
