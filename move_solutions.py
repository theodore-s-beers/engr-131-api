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
SUBMODULE_BASE_PATH = Path("vendor") / "course-content"

#
# Functions
#


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Copy solution files.")
    parser.add_argument(
        "--branch",
        type=str,
        default=DEFAULT_BRANCH,
        help="Specify the submodule branch to use (default: 'main').",
    )
    return parser.parse_args()


def ensure_submodule_branch(branch: str) -> None:
    """Ensure the submodule is on the correct branch."""
    try:
        # Change directory to the submodule
        submodule_dir = SUBMODULE_BASE_PATH

        # Debug: Print current branch
        print(f"Switching submodule to branch: {branch}", file=sys.stderr)

        # Check if the submodule exists
        if not submodule_dir.exists():
            print(
                "Submodule directory does not exist. Did you initialize the submodule?",
                file=sys.stderr,
            )
            sys.exit(1)

        # Run Git commands to ensure the submodule is on the correct branch
        subprocess.run(["git", "-C", str(submodule_dir), "fetch"], check=True)
        subprocess.run(
            ["git", "-C", str(submodule_dir), "checkout", branch], check=True
        )
        subprocess.run(
            ["git", "-C", str(submodule_dir), "pull", "origin", branch], check=True
        )

    except subprocess.CalledProcessError as e:
        print(f"Error checking out branch {branch} in submodule: {e}", file=sys.stderr)
        sys.exit(1)


def get_solution_paths(branch: str) -> list[Path]:
    """Get solution paths for a given branch."""
    branch_path = SUBMODULE_BASE_PATH

    # Debug: Print branch path
    print(f"Looking for solution files in: {branch_path}", file=sys.stderr)

    paths = [
        path
        for path in branch_path.rglob("*_q.py")
        if "blah" not in path.parts
        and "_solutions" in path.parts
        and "autograder" in path.parts
    ]

    if not paths:
        print(f"No solution files found in branch path: {branch_path}", file=sys.stderr)

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
    args = parse_args()  # Get command-line arguments
    branch = args.branch  # Use branch from command-line args

    # Ensure the submodule is checked out to the correct branch
    ensure_submodule_branch(branch)

    # Get the solution paths and process
    paths = get_solution_paths(branch)
    solutions = get_module_details(paths)
    copy_files(solutions)


if __name__ == "__main__":
    main()
