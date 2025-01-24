"""
scoring_utils.py

This module provides utility functions and classes for dynamically loading modules,
calculating scores for assignments, and handling responses for academic questions.

Classes:
    - Score: A data class to represent the maximum points and earned points for a question or assignment.

Functions:
    - load_module(path: str) -> Optional[ModuleType]:
        Dynamically loads a Python module based on the provided path.

    - calculate_score(term: str, assignment: str, question: str, responses: dict) -> Score | str:
        Calculates the score for a given question based on the provided responses.

Dependencies:
    - importlib: For dynamic module importing.
    - dataclasses: To define the Score class.
    - types.ModuleType: For type hinting loaded modules.
    - typing.Optional: To handle optional return types.
"""

import importlib
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Optional


@dataclass
class Score:
    """
    A data class to represent the score of a question or assignment.

    Attributes:
        max_points (int): The maximum possible points for the question or assignment.
        points_earned (int): The points earned by the student.
    """

    max_points: float
    points_earned: float


def load_module(path: str) -> Optional[ModuleType]:
    """
    Dynamically loads a Python module based on the provided path.

    Args:
        path (str): The module path to load (e.g., ".solutions.Fall_2024.assignment1").

    Returns:
        Optional[ModuleType]: The loaded module object if found, otherwise None.

    Exceptions:
        - Catches ModuleNotFoundError and returns None if the module is not found.

    Example Usage:
        >>> module = load_module(".solutions.Fall_2024.assignment1")
        >>> if module:
        ...     print("Module loaded successfully")
        ... else:
        ...     print("Module not found")
    """
    try:
        # Attempt to import the module dynamically
        return importlib.import_module(path, package="app")
    except ModuleNotFoundError:
        # Return None if the module does not exist
        return None


def calculate_score(
    term: str,
    week: str,
    assignment: str,
    question: str,
    responses: dict,
) -> dict[str, tuple[float, float]] | str:
    """
    Calculates the score for a given question based on the provided responses.

    Args:
        term (str): The academic term associated with the question (e.g., "Fall_2024").
        assignment (str): The assignment title or identifier (e.g., "assignment1").
        question (str): The specific question identifier within the assignment.
        responses (dict): A dictionary containing the student's responses.
                          Keys represent the question parts, and values are the student's answers.

    Returns:
        Score: An object containing the maximum possible points and the points earned by the student.
        str: An error message if the term, assignment, question, or responses are invalid.

    Error Handling:
        - Returns a string error message if:
            - The term, assignment, or question is invalid (module not found).
            - The solution or points are missing from the question module.
            - The submission is incomplete (missing responses for expected keys).

    Raises:
        None: All errors are returned as strings for handling by the calling code.

    Example Usage:
        >>> calculate_score(
                term="Fall_2024",
                assignment="assignment1",
                question="q1",
                responses={"part1": "answer1", "part2": "answer2"}
            )
        Score(max_points=10, points_earned=8)
    """
    term_module = load_module(f".solutions.{term}")
    if not term_module:
        return f"Invalid term: {term}"

    week_module = load_module(f".solutions.{term}.{week}")
    if not week_module:
        return f"Invalid week: {week}"

    assignment_module = load_module(f".solutions.{term}.{week}.{assignment}")
    if not assignment_module:
        return f"Invalid assignment: {assignment}"

    question_module = load_module(f".solutions.{term}.{week}.{assignment}.{question}")
    if not question_module:
        return f"Invalid question: {question}"

    try:
        solutions: dict[str, Any] = question_module.solutions
        points: list[float] = question_module.total_points
    except AttributeError:
        return "Error fetching solution"

    scores = {}

    for i, (k, v) in enumerate(solutions.items()):
        if k not in responses:
            # return "Incomplete submission"
            continue  # TODO: Revisit this logic

        if responses[k] == v:
            scores[k] = (points[i], points[i])
        elif isinstance(responses[k], list) and sorted(responses[k]) == sorted(v):
            print("Found correct list response out of order")
            scores[k] = (points[i], points[i])
        else:
            scores[k] = (0, points[i])

    return scores
