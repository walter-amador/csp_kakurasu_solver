# Constraint Satisfaction Problem (CSP) Solver for Kakuraso Puzzles

This repository contains a Python implementation of a Constraint Satisfaction Problem (CSP) solver designed to solve Kakuraso puzzles. Kakuraso is a logic puzzle that requires filling a grid with numbers while adhering to specific constraints.

## Running the project
1. Clone the repository:
   ```bash
   git clonehttps://github.com/walter-amador/csp_kakurasu_solver.git
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Run the solver:
   ```bash
   python3 interface.py
   ```

## Txt file format
1. Row one: Number of rows and columns (e.g., `5` for a 5x5 grid).
2. Row two: Row constraints (e.g., `3 2 1 0 4`).
3. Row three: Column constraints (e.g., `2 3 1 4 0`).