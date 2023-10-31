"""
Who has better verbal memory, you or your computer?
Unfortunately, your computer wins here... good luck,
you will need it. You need to store the words in
your brain with limited working capacity. The computer
uses a few bits... RIP!
"""
import itertools
import random
import statistics
from collections import namedtuple

from selenium.webdriver.common.by import By

import main
from utils import DATA_FOLDER, get_log_function, log_date_time


VOWELS = set("aeiou")
# Interval at which to output the current number of points.
POINTS_DISPLAY_INTERVAL = 100
# Small chance to force a mistake to avoid going on forever.
FAILURE_RATE = 0.002
# Up to how many of the most commonly seen words to display.
MOST_COMMON_COUNT = 10
# How many lives the game starts with.
LIVES = 3
LOG = DATA_FOLDER / "verbal.txt"


VerbalResult = namedtuple(
    "VerbalResult",
    ("score", "most_common", "unique_count", "duplicate_count",
     "average_word_length", "longest", "shortest", "most_vowels",
     "most_consonants", "biggest_gap", "smallest_gap")
)
MostCommon = namedtuple("MostCommon", ("word", "count"))
log = get_log_function(LOG)


def count_vowels(word: str) -> int:
    """Returns the number of vowels (aeiou) in a word."""
    return sum(char in VOWELS for char in word)


def count_consonants(word: str) -> int:
    """Returns the number of consonants in a word."""
    return sum(char.isalpha() and char not in VOWELS for char in word)


def get_verbal_result(words: dict[str, list[int]], score: int) -> VerbalResult:
    """Generates the verbal memory result and returns it."""
    unique_count = len(words)
    # Number of word occurrences which were not the first for a given word.
    duplicate_count = sum(map(len, words.values())) - unique_count
    try:
        average_word_length = statistics.mean(map(len, words))
    except statistics.StatisticsError:
        # No words for some reason, leading to an incomptable mean.
        average_word_length = None
    # Various metrics for the words that were generated in the test.
    most_common = []
    longest = None
    shortest = None
    most_vowels = None
    most_consonants = None
    biggest_gap = None
    smallest_gap = None
    for word, indexes in words.items():
        # The number of indexes a word appears at.
        count = len(indexes)
        # Adds the word to the most common count if
        # the most common count is not full yet or it is
        # greater than the current last one in the list.
        if (
            len(most_common) < MOST_COMMON_COUNT
            or count > most_common[-1].count
        ):
            # Finds the correct position to insert into else the end.
            for i, common in enumerate(most_common):
                if count > common.count:
                    most_common.insert(i, MostCommon(word, count))
                    break
            else:
                most_common.append(MostCommon(word, count))
            if len(most_common) > MOST_COMMON_COUNT:
                # Remove the one now no longer in the top few.
                most_common.pop()
        if longest is None or len(word) > len(longest):
            longest = word
        if shortest is None or len(word) < len(shortest):
            shortest = word
        vowels = count_vowels(word)
        if most_vowels is None or vowels > most_vowels[1]:
            most_vowels = (word, vowels)
        consonants = count_consonants(word)
        if most_consonants is None or consonants > most_consonants[1]:
            most_consonants = (word, consonants)
        # Processes all gaps between instances to see if any
        # are particularly small or big.
        for i1, i2 in itertools.pairwise(indexes):
            # Gap means number of other words between the same word
            # occurring again.
            # E.g. cat, dog, duck, cat. The gap for cat is 2, not 3.
            gap = i2 - i1 - 1
            if biggest_gap is None or gap > biggest_gap[1]:
                biggest_gap = (word, gap)
            if smallest_gap is None or gap < smallest_gap[1]:
                smallest_gap = (word, gap)
    return VerbalResult(
        score, most_common, unique_count, duplicate_count,
        average_word_length, longest, shortest, most_vowels,
        most_consonants, biggest_gap, smallest_gap)


def verbal(driver: "main.ComputerBenchmark") -> VerbalResult:
    """Performs the verbal memory test and returns the result."""
    log_date_time(log, "Verbal memory test started at {} UTC.")
    driver.get_test("verbal-memory")
    driver.click_start()
    words = {}
    score = 0
    lives = LIVES
    index = 0
    while lives:
        try:
            word = driver.find_element(By.CLASS_NAME, "word").text
        except Exception:
            log("Error while identifying the current word.")
            break
        if random.random() < FAILURE_RATE:
            # Purposely choose the wrong button to avoid infinite words.
            button_text = "NEW" if word in words else "SEEN"
            lives -= 1
            log(f"Purposely chose the incorrect button. Lives: {lives}")
        else:
            button_text = "SEEN" if word in words else "NEW"
            score += 1
            # Displays word progress per 100 points.
            if score % POINTS_DISPLAY_INTERVAL == 0:
                log(f"{score} points reached. {len(words)} unique words.")
        try:
            driver.find_element(
                By.XPATH, f"//button[text()='{button_text}']").click()
        except Exception:
            log(f"Failed to click on the {button_text} button.")
            break
        # Register the word and increment the index anyways.
        words[word] = words.get(word, []) + [index]
        index += 1
    return get_verbal_result(words, score)
