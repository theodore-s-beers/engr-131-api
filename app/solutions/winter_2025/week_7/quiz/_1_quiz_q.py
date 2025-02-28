from typing import Any

total_points: list[float] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-pipe-instance": "`pipe1 = Pipe()`",
    "q1-2-flow-rate": "20",
    "q1-3-valve-method": "`__init__`",
    "q1-4-pipe-status": "closed",
    "q3-1-instance-vs-class": "False",
    "q3-2-class-inheritance": "True",
    "q3-3-self-keyword": "True",
    "q3-4-encapsulation": "False",
    "q2-1-class-attributes": [
        "Class attributes are shared across all instances.",
        "Class attributes can be modified at the instance level.",
        "Classes can inherit class attributes from parent classes.",
    ],
    "q2-2-object-oriented-benefits": [
        "Code reusability through inheritance.",
        "More structured and modular code.",
        "Easier to model real-world systems like pipes and valves.",
    ],
    "q2-3-class-methods": [
        "Instance methods can access both instance attributes and class attributes.",
        "An instance method must always take itself as its first parameter.",
        "An instance method can call other methods of the same class.",
    ],
    "q2-4-pipeline-maintenance": [
        "Define an `__init__` method to initialize pipe attributes.",
        "Implement methods like `open_valve()` and `close_valve()`.",
        "Using getter and setter methods to access and modify attributes.",
    ],
}
