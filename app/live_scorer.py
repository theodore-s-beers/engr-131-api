import importlib
from dataclasses import dataclass
from types import ModuleType
from typing import Optional


@dataclass
class Score:
    max_points: int
    points_earned: int


def load_module(path: str) -> Optional[ModuleType]:
    try:
        return importlib.import_module(path, package="app")
    except ModuleNotFoundError:
        return None


def calculate_score(
    term: str,
    assignment: str,
    question: str,
    responses: dict,
) -> Score | str:
    term_module = load_module(f".solutions.{term}")
    if not term_module:
        return f"Invalid term: {term}"

    assignment_module = load_module(f".solutions.{term}.{assignment}")
    if not assignment_module:
        return f"Invalid assignment: {assignment}"

    question_module = load_module(f".solutions.{term}.{assignment}.{question}")
    if not question_module:
        return f"Invalid question: {question}"

    try:
        solution: dict = question_module.solution
        points_per_part: int = question_module.points_per_part
    except AttributeError:
        return "Error fetching solution"

    max_points: int = len(solution) * points_per_part

    points_earned = 0

    for k, v in solution.items():
        if k not in responses:
            return "Incomplete submission"

        if responses[k] == v:
            points_earned += points_per_part

    return Score(max_points=max_points, points_earned=points_earned)
