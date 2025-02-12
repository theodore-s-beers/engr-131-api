from typing import Any

total_points: float = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-helvetica-name-change": 'A method like `update_name(self, new_name)`',
    "q1-2-font-weight-update": '`Bold`',
    "q3-1-modifying-instance-attributes": 'True',
    "q3-2-change-statements-property": 'False',
    "q3-3-instance-vs-class-attributes": 'False',
    "q2-1-font-change-methods": ['Using `self.attribute = new_value` inside the method.', 'Using setter decorators.', 'Naming the method something clear, like `set_weight(new_weight)`.'],
    "q2-2-font-style-adjustments": ['`def change_font(self, new_name)`', '`def adjust_size(self, new_size)`', '`def update_style(self, new_style)`'],
}
