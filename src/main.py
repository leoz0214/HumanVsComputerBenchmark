"""
Main module of the program.

Creator Note:
This mini programming project serves as a break from the madness of
recent larger projects, and also a chance to recap web automation!
"""
import sys
from contextlib import suppress
from typing import Callable

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Wait

import aim
import chimp
import number
import reaction
import sequence
import typing_
import verbal
import visual


# The Human Benchmark website.
DOMAIN = "https://humanbenchmark.com"
# Menu options each displayed on a separate line.
OPTIONS = "\n".join((
    "1) Reaction Time",
    "2) Sequence Memory",
    "3) Chimp Test",
    "4) Aim Trainer",
    "5) Typing Speed",
    "6) Verbal Memory",
    "7) Number Memory",
    "8) Visual Memory",
    "Q) Quit"
))


def format_seconds(seconds: float) -> str:
    """Converts seconds to SS, MM:SS, HH:MM:SS as appropriate."""
    seconds = round(seconds, 2)
    if seconds < 60:
        return f"{seconds}s"
    hours = seconds // 3600
    minutes = seconds // 60 % 60
    seconds = seconds % 60
    seconds_display = str(seconds).zfill(2)
    if not hours:
        return f"{str(minutes).zfill(2)}:{seconds_display}"
    return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{seconds_display}"


def yes_or_no(prompt: str) -> bool:
    """Asks the user a yes or no question, requiring y/n as a response."""
    while True:
        response = input(f"{prompt} [Y/N]: ").strip().lower()
        if response in ("y", "ye", "yes", "yea", "yeah", "yep", "ya"):
            return True
        if response in ("n", "na", "no", "nah", "nope"):
            return False
        print("Unrecognised input.")


def get_mappings(driver: "ComputerBenchmark") -> dict[tuple[str], Callable]:
    """
    Maps various user inputs to commands.
    Tuple keys allow multiple inputs to point to the same command.
    """
    return {
        ("1", "one", "reaction", "reaction time"): driver.reaction_time,
        ("2", "two", "sequence", "sequence memory"): driver.sequence,
        ("3", "three", "chimp", "chimp test"): driver.chimp,
        ("4", "four", "aim", "aim trainer"): driver.aim,
        ("5", "five", "typing", "typing speed"): driver.typing,
        ("6", "six", "verbal", "verbal memory"): driver.verbal,
        ("7", "seven", "number", "number memory"): driver.number,
        ("8", "eight", "visual", "visual memory", "memory"): driver.visual,
        ("q", "quit", "close", "exit", "leave", "terminate"): terminate
    }


def terminate() -> None:
    """Quits the program."""
    print("Program terminated.")
    sys.exit(0)


class ComputerBenchmark(Chrome):
    """Driver which allows Human/Computer Benchmark to be run."""

    def __init__(self, headless: bool = False) -> None:
        options = ChromeOptions()
        # Do not clutter console with random messages.
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging", "enable-automation"])
        options.add_argument("--log-level=3")
        if headless:
            options.add_argument("--headless")
        super().__init__(options=options)
        # Needed for many of the challenges to function correctly.
        self.maximize_window()
        self.get(DOMAIN)
        # Attempts to agree to cookies several times before giving up.
        for _ in range(3):
            with suppress(WebDriverException):
                self.wait(
                    (By.XPATH, "//span[text()='AGREE']"),
                    until=EC.element_to_be_clickable).click()
                break
        else:
            raise RuntimeError("Failed to accept cookies.")
    
    def get_test(self, test_name: str) -> None:
        """Loads a particular test, by the last part of the URL."""
        self.get(f"{DOMAIN}/tests/{test_name}")
    
    def click_start(self, start_button_text: str = "Start") -> None:
        """Clicks on the start button of a test."""
        start_button = self.wait(
            (By.XPATH, f"//button[text()='{start_button_text}']"))
        start_button.click()

    def wait(
        self, locator: tuple[By, str],
        timeout: int | float = 15, poll: float = 0.1,
        until = EC.presence_of_element_located
    ) -> WebElement:
        """Wrapper for simplifying the wait syntax."""
        return Wait(self, timeout, poll).until(until(locator))

    def reaction_time(self) -> None:
        """Entire reaction time test process from start to finish."""
        reaction_time = reaction.reaction_time(self)
        if reaction_time.mean is None:
            return
        reaction.log(f"Mean: {reaction_time.mean}ms")
        geometric_mean = round(reaction_time.geometric_mean, 1)
        reaction.log(f"Geometric mean: {geometric_mean}ms")
        reaction.log(f"Median: {reaction_time.median}ms")
        reaction.log(f"Best: {reaction_time.best}ms")

    def sequence(self) -> None:
        """Entire sequence test process from start to finish."""
        sequence_result = sequence.sequence(self)
        sequence.log(f"Score: {sequence_result.score}")
        sequence.log(f"Final sequence:\n{sequence_result.final_sequence}")
        longest_sub_sequence = sequence_result.longest_sub_sequence
        if len(longest_sub_sequence) >= 2:
            sequence.log(f"Longest sub-sequence: {longest_sub_sequence}")
    
    def chimp(self) -> None:
        """Entire chimp test process from start to finish."""
        chimp_result = chimp.chimp(self)
        is_max = chimp_result.numbers == chimp.MAX_NUMBERS
        chimp.log(f"Final numbers: {chimp_result.numbers} "
            f"{'(max)' if is_max else ''}")
        if not chimp_result.numbers:
            return
        time_taken = format_seconds(chimp_result.seconds)
        chimp.log(f"Time taken: {time_taken}")
        chimp.log(f"Squares: {chimp_result.squares}")
        squares_per_second = round(chimp_result.squares_per_second, 2)
        chimp.log(f"Squares per second: {squares_per_second}")
        chimp.log("Island counts:")
        for numbers, grid in enumerate(chimp_result.grids, 4):
            chimp.log(f"{numbers} numbers - {len(grid.islands)}")
    
    def aim(self) -> None:
        """Entire aim test process from start to finish."""
        aim_result = aim.aim_trainer(self)
        is_max = aim_result.targets == aim.TARGETS
        aim.log(
            f"Targets hit: {aim_result.targets} {'(max)' if is_max else ''}")
        if not aim_result.targets:
            return
        time_taken = format_seconds(aim_result.seconds)
        aim.log(f"Time taken: {time_taken}")
        aim.log(f"{round(aim_result.ms_per_target, 1)}ms / target")
        distance = aim_result.distance
        if distance.mean is None:
            return
        aim.log(f"Total distance: {round(distance.total, 2)}px")
        aim.log(f"Mean distance: {round(distance.mean, 2)}px")
        aim.log(f"Median distance: {round(distance.median, 2)}px")
        aim.log(f"Minimum distance: {round(distance.min, 2)}px")
        aim.log(f"Maximum distance: {round(distance.max, 2)}px")
    
    def typing(self) -> None:
        """Entire typing test process from start to finish."""
        typing_result = typing_.typing_speed(self)
        typing_.log(f"Text:\n{typing_result.text}")
        typing_.log(f"Time taken: {round(typing_result.ms)}ms")
        typing_.log(f"{round(typing_result.words_per_min, 2)} WPM")
        typing_.log(f"{round(typing_result.chars_per_min, 2)} CPM")
        typing_.log(f"Words: {typing_result.word_count}")
        typing_.log(f"Characters: {typing_result.character_count}")
        average_word_length = round(typing_result.average_word_length, 2)
        typing_.log(f"Average word length: {average_word_length}")
        typing_.log(f"=== Difficulty / 100 ===")
        difficulty = typing_result.difficulty_score
        typing_.log(f"Repeated words: {round(difficulty.repeated_words, 2)}")
        typing_.log(f"Capital letters: {round(difficulty.capital_letters, 2)}")
        typing_.log(f"Punctuation: {round(difficulty.punctuation, 2)}")
        typing_.log(f"OVERALL: {round(difficulty.overall, 2)}")
    
    def verbal(self) -> None:
        """Entire verbal memory test from start to finish."""
        verbal_result = verbal.verbal(self)
        verbal.log(f"Score: {verbal_result.score}")
        if not verbal_result.score:
            return
        verbal.log(f"Unique words: {verbal_result.unique_count}")
        verbal.log(f"Duplicates: {verbal_result.duplicate_count}")
        average_word_length = round(verbal_result.average_word_length, 2)
        verbal.log(f"Average word length: {average_word_length}")
        longest = verbal_result.longest
        verbal.log(f"Longest word: {longest} ({len(verbal_result.longest)})")
        shortest = verbal_result.shortest
        verbal.log(f"Shortest word: {shortest} ({len(shortest)})")
        most_vowels, count = verbal_result.most_vowels
        verbal.log(f"Most vowels: {most_vowels} ({count})")
        most_consonants, count = verbal_result.most_consonants
        verbal.log(f"Most consonants: {most_consonants} ({count})")
        biggest_gap, size = verbal_result.biggest_gap
        verbal.log(f"Biggest gap in seeing: {biggest_gap} ({size})")
        smallest_gap, size = verbal_result.smallest_gap
        verbal.log(f"Smallest gap in seeing: {smallest_gap} ({size})")
        verbal.log(f"Most seen words:")
        for i, most_common in enumerate(verbal_result.most_common, 1):
            verbal.log(f"{i}. {most_common.word} ({most_common.count})")
    
    def number(self) -> None:
        """Entire number memory test from start to finish."""
        number_result = number.number(self)
        number.log(f"Score: {number_result.score}")
        number.log(f"Seen numbers:\n{number_result.numbers}")
        number.log(f"Total digits: {number_result.total_digits}")
        if not number_result.score:
            return
        number.log("Digit breakdown:")
        for digit, count in number_result.digit_breakdown.items():
            percentage = round(count / number_result.total_digits * 100, 2)
            number.log(f"{digit} - {count} ({percentage}%)")
    
    def visual(self) -> None:
        """Entire visual memory test from start to finish."""
        visual_result = visual.visual(self)
        visual.log(f"Score: {visual_result.score}")
        visual.log(f"Total squares: {visual_result.total_squares}")
        if not visual_result.score:
            return
        visual.log(f"Island counts:")
        for level, board in enumerate(visual_result.boards, 1):
            visual.log(f"Level {level}: {len(board.islands)}")


def main() -> None:
    """Main procedure of the program."""
    print("=== Human/Computer Benchmark Automation ===")
    headless = not yes_or_no("Display window?")
    if not headless:
        print("If you manipulate the window, expect some glitches!")
    else:
        print("Trust the program - the window is there, but hidden!")
    print("Initialising program...")
    with ComputerBenchmark(headless=headless) as driver:
        print("Ready to go!")
        mappings = get_mappings(driver)
        while True:
            option = input(f"Select Mode:\n{OPTIONS}\n> ").strip().lower()
            for inputs, command in mappings.items():
                if option in inputs:
                    command()
                    break
            else:
                print("Invalid input.")
            print()


if __name__ == "__main__":
    main()
