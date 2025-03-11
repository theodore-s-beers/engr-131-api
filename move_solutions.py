import argparse
import os
import shutil
import subprocess  # To handle Git commands for the submodule
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

# Optionally specify a branch via an environment variable or argument
DEFAULT_BRANCH = os.getenv("BRANCH", "main")  # Default branch is "main"

BASE_PATH = Path("app") / "solutions" / TERM
SUBMODULE_BASE = Path("vendor") / "course-content"

#
# Functions
#


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy solution files")

    parser.add_argument(
        "--branch",
        type=str,
        default=DEFAULT_BRANCH,
        help="Specify the submodule branch to use (default 'main')",
    )

    return parser.parse_args()


def ensure_submodule_branch(branch: str) -> None:
    try:
        if not SUBMODULE_BASE.exists():
            print(
                "Submodule directory does not exist. Did you initialize the submodule?",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Switching submodule to branch: {branch}", file=sys.stderr)

        actual_branches = subprocess.run(
            ["git", "-C", str(SUBMODULE_BASE), "branch", "-r"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout

        if f"origin/{branch}" not in actual_branches:
            print(
                f"Branch {branch} does not exist in the remote repository",
                file=sys.stderr,
            )
            sys.exit(1)

        # Run Git commands to ensure the submodule is on the correct branch
        subprocess.run(["git", "-C", str(SUBMODULE_BASE), "fetch"], check=True)
        subprocess.run(["git", "-C", str(SUBMODULE_BASE), "switch", branch], check=True)
        subprocess.run(
            ["git", "-C", str(SUBMODULE_BASE), "pull", "origin", branch], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error checking out submodule branch {branch}: {e}", file=sys.stderr)
        sys.exit(1)


def get_solution_paths() -> list[Path]:
    paths = [
        path
        for path in SUBMODULE_BASE.rglob("*_q.py")
        if "jupyterbook" in path.parts
        and "_solutions" in path.parts
        and "autograder" in path.parts
        and "blah" not in path.parts
    ]

    if not paths:
        print("No solution files found", file=sys.stderr)
        sys.exit(1)

    return paths


def get_module_details(paths: list[Path]) -> dict[Path, SolutionDetails]:
    solutions: dict[Path, SolutionDetails] = {}

    for path in paths:
        try:
            week_index = next(
                i
                for i, part in enumerate(path.parts)
                if part.startswith("week")
                or part.startswith("midterm")
                or part.startswith("practicefinal")
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


def switch_to_main() -> None:
    try:
        print("Switching back to main branch...", file=sys.stderr)

        subprocess.run(["git", "-C", str(SUBMODULE_BASE), "switch", "main"], check=True)
        subprocess.run(
            ["git", "-C", str(SUBMODULE_BASE), "pull", "origin", "main"], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error switching to main branch: {e}", file=sys.stderr)
        sys.exit(1)


#
# Execute
#


def main() -> None:
    args = parse_args()
    branch = args.branch  # Use branch from command-line args (default "main")

    # Ensure submodule is checked out to correct branch
    ensure_submodule_branch(branch)

    # Get solution paths and process
    paths = get_solution_paths()
    solutions = get_module_details(paths)
    copy_files(solutions)

    # Switch back to main branch
    switch_to_main()


if __name__ == "__main__":
    main()
