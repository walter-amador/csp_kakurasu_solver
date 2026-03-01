"""
Kakurasu Batch Puzzle Generator

Generates multiple Kakurasu puzzles of varying sizes and saves them to a single .txt file.
Each puzzle occupies exactly two consecutive lines:
  Line 1: comma-separated target row sums
  Line 2: comma-separated target column sums

Usage:
  python kakurasu_batch_generator.py <quantity> <size1> [size2 ...] [options]

Examples:
  python kakurasu_batch_generator.py 6 5 7 9
  python kakurasu_batch_generator.py 10 5 9 --output my_puzzles.txt --seed 42
  python kakurasu_batch_generator.py 9 5 7 9 --distribute even
"""

import random
import argparse


def generate_grid(n: int) -> list[list[int]]:
    """Generate a random n x n binary grid, ensuring every row and column has
    at least one filled cell so no sum is zero."""
    grid = [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]

    # Guarantee no all-zero row
    for i in range(n):
        if not any(grid[i]):
            grid[i][random.randrange(n)] = 1

    # Guarantee no all-zero column
    for j in range(n):
        if not any(grid[i][j] for i in range(n)):
            grid[random.randrange(n)][j] = 1

    return grid


def compute_sums(grid: list[list[int]]) -> tuple[list[int], list[int]]:
    """
    Kakurasu rules:
      - Row clue for row i  = sum of (j+1) for each filled cell in that row  (column weights are 1-based)
      - Col clue for col j  = sum of (i+1) for each filled cell in that col  (row weights are 1-based)
    """
    n = len(grid)
    row_sums = [sum((j + 1) * grid[i][j] for j in range(n)) for i in range(n)]
    col_sums = [sum((i + 1) * grid[i][j] for i in range(n)) for j in range(n)]
    return row_sums, col_sums


def generate_kakurasu(n: int) -> tuple[list[int], list[int]]:
    """Return (row_sums, col_sums) for a freshly generated n x n puzzle."""
    grid = generate_grid(n)
    return compute_sums(grid)


def build_size_sequence(quantity: int, sizes: list[int], distribute: str) -> list[int]:
    """
    Build the ordered list of sizes for each puzzle.

    distribute='even'   – cycle through sizes in order, distributing as
                          evenly as possible across all requested sizes.
    distribute='random' – pick a size uniformly at random for each puzzle.
    """
    if distribute == "even":
        return [sizes[i % len(sizes)] for i in range(quantity)]
    else:  # random
        return [random.choice(sizes) for _ in range(quantity)]


def main(quantity: int, sizes: list[int], output: str, seed: int | None, distribute: str):

    size_sequence = build_size_sequence(quantity, sizes, distribute)

    puzzles_written = 0
    size_counts: dict[int, int] = {}

    with open(output, "w") as f:
        for idx, size in enumerate(size_sequence):
            row_sums, col_sums = generate_kakurasu(size)
            f.write(",".join(map(str, row_sums)) + "\n")
            f.write(",".join(map(str, col_sums)) + "\n")
            size_counts[size] = size_counts.get(size, 0) + 1
            puzzles_written += 1

    # Summary
    print(f"Generated {puzzles_written} puzzle(s) -> {output}")
    print("Size breakdown:")
    for size in sorted(size_counts):
        print(f"  {size}x{size}: {size_counts[size]} puzzle(s)")


if __name__ == "__main__":
    # 10 puzzles of size 5x5
    main(
        quantity=10,
        sizes=[5],
        output="./batch_puzzles/kakurasu_5x5_puzzles.txt",
        seed=None,
        distribute="even",
    )
    # 10 puzzles of 7x7
    main(
        quantity=10,
        sizes=[7],
        output="./batch_puzzles/kakurasu_7x7_puzzles.txt",
        seed=None,
        distribute="even",
    )
    # 10 puzzles of 9x9
    main(
        quantity=10,
        sizes=[9],
        output="./batch_puzzles/kakurasu_9x9_puzzles.txt",
        seed=None,
        distribute="even",
    )
    # 3 puzzles of 20x20
    main(
        quantity=3,
        sizes=[20],
        output="./batch_puzzles/kakurasu_20x20_puzzles.txt",
        seed=None,
        distribute="even",
    )
