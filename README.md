# Human vs Computer Benchmark

## Introduction

Welcome to this mini project. I'm sure you have considered your reaction time, typing or memory before! Even better, perhaps you have even heard of [Human Benchmark](https://humanbenchmark.com), a small, lightweight website to test your abilities. Well, in a nutshell, this project is focused on **automating these tests just for fun**. The motto of the project is: *Who is faster, you or your computer?*

## General

Here are some key points regarding this project:
- Each of the 8 tests available on the site have been programmatically automated, combined with **analysis** of the results to varying degrees depending on the nature of the test.
- Upon completing an automated test, the result is also **logged in a text file** for future viewing.
- The code is written in **Python** and based around the **Selenium** framework.
- The program works both when the web browser window is displayed and not displayed (**headless**). However, you should not tamper with the window if displayed or else expect the program to malfunction. Also, headless mode is **more stable** and results in better test results overall.
- The code has been made robust, circumventing the issues caused by **banner advertisements** and the various delays in tests. Nonetheless, errors can, and will still occur. Some tests are simply more stable and easier to automate than others.
- *Remember, this is just for fun/educational purposes! There is no real-world value to this project.*

More technical points:
- Whilst the project can be considered functionally useless, the source code is arguably **clean and structured**, and some nifty **algorithms** are also scattered throughout the project. Feel free to take a look at the source code and perhaps you might learn a thing or two.
- Some tests can go on for virtually forever (until memory runs out), so **random failure** is built into some tests to automatically stop the test prematurely. Modify the ```FAILURE_RATE``` constant seen at the top of relevant files to control this, setting this to 0 if wishing to go on forever.
- The logic of the program will be clearer, again by reading the source code. Otherwise, you will just have to experiment with the program to discover its finer features.

## Setup and Installation

### Operating System

The program has been tested on **Windows** and works, but should still work on **MacOS** and **Linux** since nothing in the code is OS-dependent, it appears.

### Web Browser

*Human Benchmark* is a website, so the project relies on a web driver to run, and thus a web browser. This program uses the Chrome driver. **Google Chrome** is therefore required to run this program. Unfortunately, other web browsers such as Firefox, Safari, Edge, Opera and Brave are unsupported. Feel free to modify the code to make it work on other web browsers.

### Running the Program

There are two main ways of running the program:
1. Python
2. EXE (Windows only)

#### Python

The program can of course be run directly in Python. The following requirements must be met:
- Python **3.10** and above
- The libraries as seen in [REQUIREMENTS.txt](REQUIREMENTS.txt). You can install these by running ```pip install -r REQUIREMENTS.txt``` or equivalent. A relatively new version of ```selenium``` is needed for correct functionality. Also, ```BeautifulSoup``` and ```lxml``` are used to parse HTML, used in performance critical situation where simply retrieving text through the driver is too slow.

Then, you can simply use: ```python run.py``` or equivalent, ensuring the ```src``` folder is in the same folder, and hopefully, the program works as expected.

#### EXE (Windows only)

The program can also be run using a pre-built Windows executable. As long as you have Google Chrome installed correctly, simply run the EXE as usual, and hopefully the program works as expected.

If you are concerned about security yet still want to try out the program, run through Python instead.

## Individual Tests Guide

This final section will now outline each test, ready for you to explore and play with.

### Reaction Time

The classic Human Benchmark test is determining reaction time. Reaction time is defined as the time taken to react to a given stimulus. The computer will simply detect green and click.

The 5 results are then analysed with the mean reaction time and other statistical measures calculated.

### Sequence Memory

This test involves remember a sequence which occurs on a 3x3 grid. A white square is displayed on one of the squares each step of the sequence. The sequence grows by 1 square per round. For the computer, identifying and clicking the squares is easy, but the **timing** can be difficult and cause very early losses!

If you let the sequence board have the following numbers:
[0, 1, 2]
[3, 4, 5]
[6, 7, 8]
The result provides the final sequence in terms of these numbers, the score, and also, if relevant, the longest repeating sub-sequence.

For example, the longest repeating sub-sequence of [0, 3, 8, 6, 1, 4, 5, 3, 8, 6] is [3, 8, 6]

### Chimp Test

The classic dilemma: *Are you smarter than a chimpanzee?* The chimp test involves viewing a grid with numbers displayed, and subsequently having to click the squares in ascending numerical order (with the numbers hidden). For the computer, this is ridiculously easy, and this is arguably the **most stable** test of them all.

The grids of numbers will be displayed for each level (0 indicates no square) along with the islands sizes. An island in this context is a group of positive integers connected horizontally or vertically. It can be a single number or many.

The result includes the scores and speed, along with an overview of the islands.

### Aim Trainer

A very useful test for gamers. The test involves clicking a target which moves upon each click, 30 times. This combines reaction time and hand-eye co-ordination. The computer identifies the co-ordinates of each target and clicks. It is somewhat fast, as a result.

The result consists of the score, total time taken, time per target, and even various **distance metrics** in terms of pixels (minimum distances between consecutive targets using geometry). The distance data is just above and beyond.

### Typing Speed

A nice test to see how proficient you can use a keyboard.The test simply involves typing a text as fast and accurately as possible, with the speed displayed as words per minute (WPM). The computer completes this test at **insane speeds** (no human stands a chance).

The result is more interesting than the test itself in terms of the automation. Of course, speed metrics are included. Text analysis is also provided, including character count, average word length etc.

However, the most interesting aspect of this test is the **made-up text difficulty metric**. This considers 3 factors to estimate the difficulty of a text to type for a human:
- **Repeated words** - repeated words make a text very slightly easier to type, especially when close together. The less repeated words, the harder. This has minimal effect however, so has a low weighting.
- **Capital letters** - capital letters slow you down by forcing you to use Shift, increasing the risk of a mistake. This has a noticeable effect, so has a moderate weighting.
- **Punctuation** - punctuation slows you down a lot in general, especially ones which require Shift, and/or rarely used ones. This has a big effect, so has a large weighting.

An overall difficulty score is then generated. Take this metric with a grain of salt since it is just for fun.

### Verbal Memory

Verbal relates to words. The verbal memory test is constantly receiving words and having to cateogorise them as **SEEN or NEW**, based on whether they have already been generated or not. The computer is unstoppable here since it can easily track seen words.

The result provides the score, number of unique words, average word length, and some of the most significant words: longest, shortest, most vowels, most consonants etc.

### Number Memory

The number memory test is straightforward - to remember increasingly large numbers. *The average human can remember 7 digits*. The avreage computer should be able to remember billions of digits, due to RAM of course! This increases further if considering secondary storage. Seriously though, this test is nothing for a computer.

The result includes the score and digits breakdown (frequency of the digits 0-9).

### Visual Memory

Vision relates to sight. The visual memory test displays a 2D grid of squares. Some squares will be white and displayed briefly, and must then be clicked correctly to pass the level. This test is somewhat easy for a computer to handle, but the **timing** needs to be correct. Lag will break this test for a computer.

As the levels progress, the grid and islands will be displayed, with 0 representing an OFF square and 1 representing a white square.

The notion of islands in this context is a group of 1s connected by row or column.

For example,
[1, 0, 0]
[0, 1, 1],
[1, 0, 1]
has islands of size [3, 1, 1]

The result will include the score and islands overview.

## Final Disclaimer

The code works at the time of release. However, the Human Benchmark website can, and probably will change in the future. Even small changes may break some tests, so stability cannot be guaranteed. Nonetheless, as the project is for fun, this is not a problem.
