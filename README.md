# Python Tetris Automation

A Python-based automation project that analyses a live game of Tetris from https://play.tetris.com/ in real time, determines the optimal move using a custom simulation engine, and executes the required keyboard inputs automatically.

This project was created primarily as a way to develop my Python skills through a challenging, performance-critical problem involving image processing, algorithm design, optimisation, and automation and also to beat my friends' high score.. still in progress 😂

Current highscore: 210,050

---

## Features

* Real-time game state detection from screen captures
* Binary image processing for fast board recognition
* Complete game state reconstruction from captured frames
* Custom Tetris simulation engine
* Automated move generation and keyboard input
* Modular, object-oriented codebase

---

## Technologies

* Python
* NumPy
* MSS (high-speed screen capture)
* Keyboard
* Pillow (image handling where required)

---

## Project Goals

Rather than using computer vision or machine learning, the objective was to solve the problem using deterministic algorithms.

The program continuously:

1. Captures the game window.
2. Extracts the centre pixel of each cell within the 10x20 grid which comprises the game board.
3. Reconstructs the current game state.
4. Simulates every possible placement for the active tetromino.
5. Scores each resulting board position: penalty points are given to bad moves.
6. Selects the lowest scoring move.
7. Executes the required keyboard inputs before the next game update.

The focus throughout development has been on reducing computation time while maintaining reliable move selection.

---

## Optimisation

A major focus of this project has been performance optimisation.

Examples include:

* Binary board representation instead of RGB image processing
* Efficient NumPy array operations
* Reducing unnecessary memory allocations
* Profiling and benchmarking critical sections
* Separating screen capture, game analysis and input automation into independent stages to improve responsiveness

As the project evolves, further improvements such as asynchronous execution and parallel processing may be explored.

---

## Why I Built This

I wanted a project that would force me to solve real engineering problems rather than simply follow tutorials.

Throughout development I've gained experience with:

* Algorithm design
* Performance optimisation
* Object-oriented software architecture
* Real-time image processing
* Debugging complex systems
* Python profiling and benchmarking

---

## Current Status

🚧 Active development

The automation is fully functional and continues to be refined. Current work focuses on improving simulation speed, reducing latency, and making the architecture easier to extend and maintain.

---

## Disclaimer

This project was built purely for educational purposes to explore algorithm development, optimisation techniques, and Python programming. It is not intended for competitive play or online use.

