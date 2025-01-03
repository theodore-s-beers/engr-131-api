import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

#
# Types
#


@dataclass
class SolutionDetails:
    term: str
    week: str
    category: str


#
# Consts
#

TERM = "winter_2025"  # Constant for now

BASE_PATH = Path("app") / "solutions" / TERM
SUBMODULE_PATH = Path("vendor") / "course-content"

#
# Functions
#


def get_solution_paths() -> list[Path]:
    paths = [
        path
        for path in SUBMODULE_PATH.rglob("*_q.py")
        if "_solutions" in path.parts and "autograder" in path.parts
    ]

    if not paths:
        print("No solution files found", file=sys.stderr)
        sys.exit(1)

    return paths


def get_module_details(paths: list[Path]) -> dict[Path, SolutionDetails]:
    solutions = {}

    for path in paths:
        try:
            week_index = next(
                i for i, part in enumerate(path.parts) if part.startswith("week")
            )
            week = path.parts[week_index]
            category = path.parts[week_index + 1]
        except (StopIteration, IndexError):
            print(f"Problem parsing path: {path}", file=sys.stderr)
            sys.exit(1)

        solutions[path] = SolutionDetails(term=TERM, week=week, category=category)

    return solutions


def copy_files(solutions: dict[Path, SolutionDetails]) -> None:
    for path, solution in solutions.items():
        module_dir = BASE_PATH / solution.week / solution.category
        module_dir.mkdir(parents=True, exist_ok=True)

        # Ensure __init__.py exists in each directory
        for directory in [BASE_PATH, BASE_PATH / solution.week, module_dir]:
            init_file = directory / "__init__.py"
            if not init_file.exists():
                init_file.touch()

        shutil.copy(path, module_dir / path.name)


#
# Execute
#


def main() -> None:
    paths = get_solution_paths()
    solutions = get_module_details(paths)
    copy_files(solutions)


if __name__ == "__main__":
    main()
