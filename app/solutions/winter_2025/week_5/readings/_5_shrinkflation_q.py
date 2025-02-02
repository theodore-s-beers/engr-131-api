from typing import Any

total_points: float = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-shrinkflation-prices": 'Error: `new_price` is not defined.',
    "q1-2-global-local-variables": 'The local variable takes precedence inside the function.',
    "q3-1-global-keyword": 'True',
    "q3-2-local-variables": 'True',
    "q3-3-multiple-scopes": 'True',
    "q2-1-global-and-local-variables": ['A global variable is accessible inside a function unless shadowed by a local variable.', 'A local variable is created when assigned inside a function.', 'Using the `global` keyword inside a function allows you to modify a global variable.'],
    "q2-2-shrinkflation-variables": ['A function tries to modify a global variable without declaring it as global.', 'A local variable inside a function is accessed outside the function.'],
}
