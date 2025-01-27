from typing import Any

total_points: list[float] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-what-calculates-derivatives": "`diff()`",
    "q1-2-what-calculates-integrals": "`integrate()`",
    "q1-3-what-calculates-limits": "The behavior of a function as it approaches a value",
    "q3-1-linsolve-non-linear-equations": "False",
    "q3-2-sympy-solves-nonlinear-equations": "True",
    "q3-3-dsolve-function": "True",
    "q3-4-dsolve-function-numpy": "False",
    "q2-1-what-is-the-diff-function-used-for-in-sympy": [
        "Calculate the rate of change of a function",
        "Find the slope of a curve",
        "Calculate higher-order derivatives",
    ],
    "q2-2-what-is-the-integrate-function-used-for-in-sympy": [
        "Compute the area under a curve",
        "Calculate the volume of a solid",
    ],
}
