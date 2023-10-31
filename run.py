"""Run this code to start up the app."""
import pathlib
import sys


if hasattr(sys, "_MEIPASS"):
    SRC_FOLDER = pathlib.Path(sys.executable).parent / "src"
else:
    SRC_FOLDER = pathlib.Path(__file__).parent / "src"


sys.path.append(str(SRC_FOLDER))


import main


if __name__ == "__main__":
    main.main()
