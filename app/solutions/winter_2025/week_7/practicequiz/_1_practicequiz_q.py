from typing import Any

total_points: list[float] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-machine-instance": "`machine1 = Machine()`",
    "q1-2-factory-production-count": "100",
    "q1-3-inventory-method": "`__init__`",
    "q1-4-machine-status": "running",
    "q3-1-instance-vs-class": "False",
    "q3-2-class-inheritance": "True",
    "q3-3-self-keyword": "True",
    "q3-4-encapsulation": "True",
    "q2-1-class-attributes": [
        "Class attributes are shared across all instances.",
        "Class attributes can be modified at the instance level.",
        "A class attribute can be a dictionary.",
    ],
    "q2-2-object-oriented-benefits": [
        "Code reusability through inheritance.",
        "More structured and modular code.",
        "Easier to model real-world systems like machines and inventory.",
    ],
    "q2-3-class-methods": [
        "Instance methods can access both instance attributes and class attributes.",
        "An instance method must always have `self` as its first parameter.",
        "An instance method can call other methods of the same class.",
    ],
    "q2-4-factory-maintenance": [
        "Define an `__init__` method to initialize machine attributes.",
        "Implement methods like `start_machine()` and `stop_machine()`.",
    ],
}
