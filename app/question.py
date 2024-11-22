from typing import Optional

from .live_scorer import Score, load_module


def valid_submission(
    term: str,
    assignment: str,
    question: str,
    responses: dict,
    score: Score,
) -> Optional[str]:
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
        points: list[int] = question_module.points
    except AttributeError:
        return "Error fetching solution"

    if len(responses) != len(solution):
        return "Invalid response length"

    max_points: int = sum(points)
    if score.max_points != max_points:
        return "Invalid score data"

    return None
