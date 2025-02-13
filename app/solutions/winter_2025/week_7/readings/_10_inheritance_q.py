from typing import Any

total_points: list[float] = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-player-inheritance": "Inheritance allows a class to reuse attributes and methods from another class.",
    "q1-2-quarterback-subclass": "`Patrick Mahomes 97 99`",
    "q3-1-base-class": "True",
    "q3-2-overriding-methods": "True",
    "q3-3-super-method": "False",
    "q2-1-madden-positions": [
        "Reduces code duplication by reusing attributes.",
        "Allows specialized player classes like `Quarterback` or `WideReceiver`.",
        "Makes it easy to add new player positions with different attributes.",
    ],
    "q2-2-nfl-inheritance-methods": [
        "`def __init__(self, name, rating):`",
        "`super().__init__(name, rating)`",
        "`class RunningBack(Player):`",
    ],
}
