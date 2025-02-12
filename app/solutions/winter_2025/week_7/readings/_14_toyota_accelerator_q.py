from typing import Any

total_points: list[float] = [1.0, 1.0, 1.0, 1.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-abstraction-definition": "A class that defines methods but does not implement them.",
    "q1-2-abstract-methods": "An error occurs because abstract classes cannot be instantiated.",
    "q3-1-abstract-class": "True",
    "q3-2-subclassing": "True",
    "q2-1-toyota-abstraction-failure": [
        "Abstract base classes could have enforced proper handling of acceleration overrides.",
        "Abstract methods could have required implementing fail-safe mechanisms in all subclasses.",
        "Reducing dependencies between software components could have made debugging easier.",
    ],
    "q2-2-abstraction-methods": [
        "An abstract method **must** be implemented by subclasses.",
        "Abstract methods **must** be decorated with `@abstractmethod`.",
    ],
}
