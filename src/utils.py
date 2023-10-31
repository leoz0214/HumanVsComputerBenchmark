"""General shared utilities of the program."""
import datetime as dt
import pathlib
import sys
from typing import Callable


# Folder to store the data (logs) in for the user to manually view.
if hasattr(sys, "_MEIPASS"):
    # Running EXE.
    executable_folder = pathlib.Path(sys.executable).parent
    DATA_FOLDER = executable_folder / "human_computer_benchmark_data"
else:
    # Running Python program.
    DATA_FOLDER = pathlib.Path(__file__).parent.parent / "data"


def append_text(file_path: pathlib.Path, text: str) -> None:
    """Adds text to the end of a text file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf8") as f:
        f.write(text)


def get_log_function(log_file: pathlib.Path) -> Callable:
    """Creates a log function for a given file."""
    def log(text: str, print_too: bool = True, end: str = "\n") -> None:
        append_text(log_file, f"{text}{end}")
        if print_too:
            print(text)
    return log


def log_date_time(log: Callable, message_format: str) -> None:
    """Logs the UTC date/time, from a given log and message format."""
    date_time = dt.datetime.utcnow()
    message = message_format.format(date_time)
    log(message, print_too=False)


def count_ones(
    board: list[list[int]], row: int, column: int,
    direction: tuple[int, int]
) -> int:
    """
    Counts 1s in a given direction (+/- row, +/- column), starting from a
    particular co-ordinate, sets them to 0 and returns the count.
    """
    # Translates the row and column.
    row += direction[0]
    column += direction[1]
    # Bounds check.
    if not (0 <= row < len(board) and 0 <= column < len(board[0])):
        return 0
    # Check if already 0.
    if board[row][column] == 0:
        return 0
    # Set to 0.
    board[row][column] = 0
    count = 1
    # Moves in all directions recursively and sum up 1s.
    for i in (-1, 1):
        count += count_ones(board, row, column, (i, 0))
        count += count_ones(board, row, column, (0, i))
    return count


def get_islands(board: list[list[int]]) -> list[int]:
    """
    Returns a list of island sizes in a given 2D array
    of 1s/positive ints, and 0s, smallest to largest.
    An island is where positive numbers are linked horizontally or vertically.
    For example:
    [1, 0, 1],
    [0, 1, 1],
    [1, 0, 0]
    returns [3, 1, 1].
    """
    # Makes a copy of the board to avoid mutating original board.
    board = [row.copy() for row in board]
    islands = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            # New island, a 1 is at the given co-ordinate.
            if board[i][j]:
                islands.append(count_ones(board, i, j, (0, 0)))
    return sorted(islands, reverse=True)
