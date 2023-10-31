"""
Performs the typing test. Who can type faster, you or
your computer (i.e Selenium)? Find out with this test!
"""
import itertools
import math
from collections import namedtuple

from selenium.webdriver.common.by import By

import main
from utils import DATA_FOLDER, get_log_function, log_date_time


# Capital letter rates (score - best = 0, worst = 100).
BEST_CAPITAL_LETTER_RATE = 0.01
WORST_CAPITAL_LETTER_RATE = 0.03
# How much harder each punctuation character is perceived to be.
PUNCTUATION_WEIGHTINGS = {
    " ": 0.1,
    ".": 2,
    ",": 2,
    "-": 4,
    "!": 5,
    "?": 5,
    ":": 8,
    "(": 8,
    ")": 8,
    "'": 8,
    '"': 8,
    ";": 8
}
# Punctuation constants (score - best = 0, worst = 100)
BEST_PUNCTUATION_RATE = 0.04
WORST_PUNCTUATION_RATE = 0.12
# Weighting of each category on the overall difficulty.
REPEATED_WORDS_WEIGHTING = 0.15
CAPITAL_LETTERS_WEIGHTING = 0.35
PUNCTUATION_WEIGHTING = 0.5
# Difficulty score range.
MIN_DIFFICULTY = 0
MAX_DIFFICULTY = 100
LOG = DATA_FOLDER / "typing_speed.txt"


TypingResult = namedtuple(
    "TypingResult",
    ("words_per_min", "chars_per_min", "ms", "text", "word_count",
    "character_count", "average_word_length",
    "punctuation_count", "difficulty_score")
)
DifficultyScore = namedtuple(
    "DifficultyScore",
    ("repeated_words", "capital_letters", "punctuation", "overall")
)
log = get_log_function(LOG)


def clamp_difficulty(score: float) -> float:
    """Clamps a difficulty score to avoid going out of bounds."""
    return min(max(score, MIN_DIFFICULTY), MAX_DIFFICULTY)


def get_repeated_words_difficulty(words: list[str]) -> float:
    """Returns the repeated words difficulty aspect out of 100."""
    # Determine the positions of the occurrences of each word.
    word_indexes = {}
    for i, word in enumerate(words):
        word_indexes[word] = word_indexes.get(word, []) + [i]
    repeated_words_difficulty = 50
    for word, indexes in word_indexes.items():
        if len(indexes) == 1:
            # Not repeated - not ideal.
            repeated_words_difficulty += 1
        # Each pair that occurs reduces typing complexity.
        for first, second in itertools.pairwise(indexes): 
            # Determines difficulty decrease to induce.
            # The smaller the repetition delay, the better.
            # A huge delay is instead pointless and may instead
            # even result in a tiny increase anyways.
            decrease = max(6 - math.log2(second - first), -0.5)
            repeated_words_difficulty -= decrease
    return clamp_difficulty(repeated_words_difficulty)


def get_capital_letters_difficulty(
    capital_letter_count: int, alnum_character_count: int
) -> float:
    """Returns the capital letters difficulty aspect out of 100."""
    # Finds capital letters rate and deduces a corresponding score.
    capital_letters_rate = capital_letter_count / alnum_character_count
    capital_letters_difficulty = (
        (capital_letters_rate - BEST_CAPITAL_LETTER_RATE)
        / (WORST_CAPITAL_LETTER_RATE - BEST_CAPITAL_LETTER_RATE)) * 100
    return clamp_difficulty(capital_letters_difficulty)


def get_punctuation_difficulty(
    punctuation: dict[str, int], character_count: int
) -> float:
    """Returns the punctuation difficulty aspect out of 100."""
    # Determines the number of punctuation points with each
    # character having a particular weighting i.e. " is worse than ,
    punctuation_points = 0
    for character, weighting in PUNCTUATION_WEIGHTINGS.items():
        punctuation_points += punctuation.get(character, 0) * weighting
    points_per_char = punctuation_points / character_count
    punctuation_difficulty = (
        (points_per_char - BEST_PUNCTUATION_RATE)
        / (WORST_PUNCTUATION_RATE - BEST_PUNCTUATION_RATE)) * 100
    return clamp_difficulty(punctuation_difficulty)


def get_difficulty_score(
    words: list[str], character_count: int, alnum_character_count: int,
    capital_letter_count: int, punctuation: dict[str, int]
) -> DifficultyScore:
    """
    Algorithm which rates the difficulty of an extract to type,
    for a human of course. The rating is from a scale from 0 to 100.
    Key Points:
    - Repeated words make things VERY SLIGHTLY easier.
        The smaller the repetition delay, the better.
    - Capital letters make things SLIGHTLY harder due to Shift needed.
    - Punctuation make things HARDER by quite a bit since they are lesser used.
        INCLUDE SPACE with very tiny weighting.
        Certain characters are harder than others e.g. " is very hard.
    Weightings:
    - Repeated words (15%)
        Few to no repeated words - worst case scenario.
        A large number of repeated words will minimise the difficulty.
    - Capital letters (35%)
        Very few capital letters - best case scenario.
        Lots of capital letters - worst case scenario.
    - Punctuation (50%)
        Minimal punctuation, no hard ones - best case.
        Lots of punctuation, especially hard ones - worst case.
    """
    repeated_words_difficulty = get_repeated_words_difficulty(words)
    capital_letters_difficulty = get_capital_letters_difficulty(
        capital_letter_count, alnum_character_count)
    punctuation_difficulty = (
        get_punctuation_difficulty(punctuation, character_count))
    # Computes the overall difficulty based on the specified weightings.
    overall_difficulty = (
        repeated_words_difficulty * REPEATED_WORDS_WEIGHTING
        + capital_letters_difficulty * CAPITAL_LETTERS_WEIGHTING
        + punctuation_difficulty * PUNCTUATION_WEIGHTING)
    return DifficultyScore(
        repeated_words_difficulty, capital_letters_difficulty,
        punctuation_difficulty, overall_difficulty)


def get_typing_result(words_per_min: int, text: str) -> TypingResult:
    """Generates the typing results based on WPM and test text."""
    words = []
    capital_letters_count = 0
    # Tracks punctuation counts.
    punctuation = {}
    # Last index where a space was seen (initialised as -1).
    last_space = -1
    # Space added at the end, allowing final word to be registered.
    for i, character in enumerate(f"{text} "):
        # For simplicity, consider
        # all non-alphanumeric characters as punctuation.
        if not character.isalnum():
            punctuation[character] = punctuation.get(character, 0) + 1
        if character == " ":
            # Strips the word of any punctuation.
            word = "".join(filter(str.isalnum, text[last_space+1:i]))
            # Only add the word if it is really a word (or number...)
            if word:
                words.append(word.lower())
            last_space = i
        if character.isupper():
            capital_letters_count += 1
    word_count = len(words)
    character_count = len(text)
    # Counts the number of alphanumeric characters by summing the word lengths.
    alnum_count = sum(map(len, words))
    average_word_length = alnum_count / word_count
    ms = word_count / words_per_min * 60000
    chars_per_min = character_count / ms * 60000
    punctuation_count = sum(punctuation.values())
    difficulty_score = get_difficulty_score(
        words, character_count, alnum_count,
        capital_letters_count, punctuation)
    return TypingResult(
        words_per_min, chars_per_min, ms, text, word_count, character_count,
        average_word_length, punctuation_count, difficulty_score)


def typing_speed(driver: "main.ComputerBenchmark") -> TypingResult:
    """Performs the typing test and returns the result."""
    log_date_time(log, "Typing speed test started at {} UTC.")
    driver.get_test("typing")
    textbox = driver.wait((By.CLASS_NAME, "letters"))
    # Extract the text and simply type it all out at once. That is all
    # for the web automation part of this task.
    text = textbox.text
    textbox.send_keys(text)
    # Deduce the WPM displayed on the page.
    result_element = driver.wait((By.TAG_NAME, "h1"))
    words_per_min = int(result_element.text.removesuffix("wpm"))
    return get_typing_result(words_per_min, text)
