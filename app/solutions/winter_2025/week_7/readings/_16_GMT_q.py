from typing import Any

total_points: list[float] = [1.0, 1.0, 1.0, 1.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-multiple-inheritance-definition": "A class that inherits from more than one parent class.",
    "q1-2-rolex-multiple-parents": "`Displaying local time.`",
    "q3-1-mro-sequence": "True",
    "q3-2-single-inheritance-requirement": "False",
    "q2-1-rolex-inheritance-benefits": [
        "Combines functionalities from different classes (e.g., time display and GMT tracking).",
        "Allows the class to inherit and override methods from multiple sources.",
        "Simplifies code reuse by leveraging existing class behaviors.",
    ],
    "q2-2-rolex-diamond-mix": [
        "`class Timekeeping:`",
        "`class LuxuryBrand:`",
        "`class GoldPlated:`",
    ],
}
