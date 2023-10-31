"""
Are you smarter than a chimpanzee?
Is the computer smarter than a chimpanzee?
Who is the smartest: you, your computer or your chimpanzee?

Of course, the computer will win on this test!
The computer is beyond a chimpanzee or human. RIP!
"""
from collections import namedtuple
from timeit import default_timer as timer

import lxml
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

import main
from utils import DATA_FOLDER, get_log_function, get_islands, log_date_time


# The starting number count for the first level, followed
# by the final number count for the last level.
MIN_NUMBERS = 4
MAX_NUMBERS = 40
LOG = DATA_FOLDER / "chimp.txt"


ChimpResult = namedtuple(
    "ChimpResult",
    ("numbers", "grids", "seconds", "squares", "squares_per_second")
)
Grid = namedtuple("Grid", ("grid", "islands"))
log = get_log_function(LOG)


def get_chimp_result(grids: list[Grid], time_taken: float) -> ChimpResult:
    """Generates the chimp test result."""
    if not grids:
        return ChimpResult(0, [], time_taken, 0, 0)
    numbers = len(grids) + MIN_NUMBERS - 1
    squares = (
        (numbers * (numbers + 1)) // 2
        - ((MIN_NUMBERS - 1) * MIN_NUMBERS) // 2)
    squares_per_second = squares / time_taken
    return ChimpResult(numbers, grids, time_taken, squares, squares_per_second)


def chimp(driver: "main.ComputerBenchmark") -> ChimpResult:
    """Performs the chimp test and returns the result."""
    log_date_time(log, "Chimp test started at {} UTC.")
    driver.get_test("chimp")
    driver.click_start("Start Test")
    start = timer()
    grids = []
    for numbers in range(MIN_NUMBERS, MAX_NUMBERS + 1):
        try:
            soup = BeautifulSoup(driver.page_source, "lxml")
            grid = [
                [int(div.get("data-cellnumber", 0))
                    for div in row.find_all("div", recursive=False)]
                for row in soup.find_all(class_="css-k008qs")]
        except Exception:
            log("Error while identifying grid!")
            return get_chimp_result(grids, timer() - start)
        for number in range(1, numbers + 1):
            try:
                square = driver.find_element(
                    By.XPATH, f"//div[@data-cellnumber='{number}']")
                # Performs a JavaScript click since it works.
                # This makes the test very reliable and fast.
                driver.execute_script("arguments[0].click();", square)
            except Exception:
                log("Error while clicking!")
                return get_chimp_result(grids, timer() - start)
        log(f"{numbers} numbers done.")
        for row in grid:
            log(row)
        islands = get_islands(grid)
        log(f"Islands: {islands}")
        grids.append(Grid(grid, islands))
        if numbers == MAX_NUMBERS:
            return get_chimp_result(grids, timer() - start)
        try:
            driver.find_element(
                By.XPATH, "//button[text()='Continue']").click()
        except Exception:
            log("Error while continuing!")
            return get_chimp_result(grids, timer() - start)
