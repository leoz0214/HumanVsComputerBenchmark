"""
Who has better aim, you (a mortal), or your computer?
Unfortunately, this is quite hopeless. The computer does
not even need to know the coordinates/location! Good luck!
"""
import itertools
import math
import statistics
import time
from collections import namedtuple
from timeit import default_timer as timer

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import main
from utils import DATA_FOLDER, get_log_function, log_date_time


TARGETS = 30
MIN_Y_TO_USE_ACTION_CHAINS = 375
# Radius of each circular target in pixels.
RADIUS = 50
LOG = DATA_FOLDER / "aim.txt"


AimResult = namedtuple(
    "AimResult",
    ("targets", "seconds", "ms_per_target", "coordinates", "distance")
)
# Distance between targets - the general results.
DistanceResult = namedtuple(
    "DistanceResult",
    ("total", "mean", "median", "min", "max")
)
log = get_log_function(LOG)


def get_distance_result(coordinates: list[tuple[int, int]]) -> DistanceResult:
    """Obtains the distance result as part of the overall aim result."""
    # The MINIMUM distances between two consecutive targets are calculated.
    # Circle 1 (x1, y1) radius r1. Circle 2 (x2, y2) radius r2.
    # Min Distance = distance between centres - r1 - r2.
    # If two circles OVERLAP, distance = 0
    distances = [
        max(math.dist(from_, to) - RADIUS * 2, 0)
        for from_, to in itertools.pairwise(coordinates)]
    if not distances:
        # Only one target hit.
        return DistanceResult(None, None, None, None, None)
    total = sum(distances)
    mean = statistics.mean(distances)
    median = statistics.median(distances)
    minimum = min(distances)
    maximum = max(distances)
    return DistanceResult(total, mean, median, minimum, maximum)


def get_aim_result(
    targets: int, seconds: float, coordinates: list[tuple[int, int]]
) -> AimResult:
    """Returns information regarding the aim trainer result."""
    if not targets:
        return AimResult(0, 0, 0, [], None)
    ms_per_target = seconds / targets * 1000
    distance = get_distance_result(coordinates)
    return AimResult(targets, seconds, ms_per_target, coordinates, distance)


def click_target(driver: "main.ComputerBenchmark") -> tuple[int, int]:
    """Clicks on the target on screen. Also returns the coordinates."""
    target = driver.wait(
        (By.XPATH, "//div[@data-aim-target='true']"), 5, 0.01)
    # The parent element contains the co-ordinate of the target.
    parent = target.find_element(By.XPATH, "..")
    # Identifies the co-ordinates of the centre of the target by
    # looking at the style attribute containing the centre.
    # Rounds to integer co-ordinates for simplicity.
    x, y = (
        round(float(n))
        for n in parent.get_attribute("style").split(",")[-4:-2])
    # The target has various divs, some which work, some which do not.
    to_click = target.find_elements(By.CLASS_NAME, "e6yfngs4")[1]
    try:
        # If False, will raise an error and the alternative method used.
        assert y < MIN_Y_TO_USE_ACTION_CHAINS
        to_click.click()
    except Exception:
        # Either y is too large (ads will intercept), or basic click fails.
        action_chain = ActionChains(driver)
        action_chain.move_to_element_with_offset(
            to_click, 0, -10).click().perform()
    return (x, y)


def get_remaining(driver: "main.ComputerBenchmark") -> int:
    """Returns the number of targets remaining to hit."""
    remaining_element = driver.find_element(By.CLASS_NAME, "css-dd6wi1")
    return int(remaining_element.text.removeprefix("Remaining"))


def aim_trainer(driver: "main.ComputerBenchmark"):
    """Performs the aim test and returns the result."""
    log_date_time(log, "Aim trainer started at {} UTC.")
    driver.get_test("aim")
    # Click the target to start.
    click_target(driver)
    coordinates = []
    start = timer()
    # Click the target n times until completion.s
    for i in range(TARGETS):
        try:
            target_coords = click_target(driver)
            log(f"{i+1}. {target_coords}")
        except Exception:
            log("Error while clicking!")
            break
        coordinates.append(target_coords)
    stop = timer()
    time.sleep(0.25)
    if "Average time per target" in driver.page_source:
        # Fully complete.
        return get_aim_result(TARGETS, stop - start, coordinates)
    # Incomplete. Something must've gone wrong.
    try:
        targets = TARGETS - get_remaining(driver)
    except Exception:
        log("Error while fetching the remaining number of targets.")
        return get_aim_result(0, 0, [])
    return get_aim_result(
        targets, stop - start, coordinates[:targets])
