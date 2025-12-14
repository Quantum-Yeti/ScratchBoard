from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QGridLayout, QPushButton, QLabel, QSizePolicy, QComboBox

from utils.resource_path import resource_path

storage_units = {
    "Byte": 1,
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4
}

speed_units = {
    "bps": 1 / 8,
    "kbps": 1024 / 8,
    "mbps": 1024**2 / 8,
    "gbps": 1024**3 / 8,
    "tbps": 1024**4 / 8
}

def convert(value, from_unit, to_unit):
    bytes_value = value * storage_units[from_unit]
    return bytes_value / storage_units[to_unit]

class SimpleCalcView(QDialog):
    """
    Minimal calculator with normal mode and outage mode.
    Outage Mode: calculate cost of service downtime based on monthly charge.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: Simple Calculator/Storage Calculator")
        self.setFixedSize(400, 500)

        self.current_expression = ""
        self.converter_mode = False

        self._create_calc_ui()

    def _create_calc_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Result label
        self.result_label = QLabel("Result:")
        self.result_label.setAlignment(Qt.AlignRight)
        self.result_label.setStyleSheet("font-size: 18px;")
        main_layout.addWidget(self.result_label)

        # Display
        self.display = QLineEdit()
        self.display.setPlaceholderText("Calculate something...")
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 22px; padding: 5px;")
        main_layout.addWidget(self.display)

        # Grid layout for buttons
        grid = QGridLayout()
        grid.setSpacing(5)

        # Mode button spanning all columns
        self.mode_button = QPushButton("Toggle Mode")
        self.mode_button.setIcon(QIcon(resource_path("resources/icons/calculate.png")))
        self.mode_button.setIconSize(QSize(32, 32))
        self.mode_button.setStyleSheet("text-align: center;")
        self.mode_button.setCheckable(True)
        self.mode_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.mode_button.setFixedHeight(50)
        self.mode_button.toggled.connect(self._toggle_converter_mode)
        grid.addWidget(self.mode_button, 0, 0, 1, 4)

        # Button definitions
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '.', '+'],
            ['=']
        ]

        for row, row_buttons in enumerate(buttons, start=1):
            for col, text in enumerate(row_buttons):
                button = QPushButton(text)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.setStyleSheet("font-size: 20px; text-align: center;")
                button.clicked.connect(lambda checked, b=text: self._on_btn_clicked(b))

                if text == "C":
                    grid.addWidget(button, row, 0)
                elif text == "=":
                    grid.addWidget(button, row, 0, 1, 4)  # span full width
                else:
                    # Calculate column index: 'C' takes 0, then 1..3 for other buttons
                    grid.addWidget(button, row, col)

        # Make all columns expand equally
        for i in range(4):
            grid.setColumnStretch(i, 1)
        for i in range(len(buttons)+1):
            grid.setRowStretch(i, 1)

        main_layout.addLayout(grid)

    def _toggle_converter_mode(self, checked):
        self.converter_mode = checked
        self.current_expression = ""
        self.display.setText("")

        if checked:
            self.from_unit = QComboBox()
            self.from_unit.addItems(list(storage_units.keys()))
            self.to_unit = QComboBox()
            self.to_unit.addItems(list(storage_units.keys()))
            self.layout().insertWidget(1, self.from_unit)
            self.layout().insertWidget(2, self.to_unit)
        else:
            self.layout().removeWidget(self.from_unit)
            self.layout().removeWidget(self.to_unit)
            self.from_unit.deleteLater()
            self.to_unit.deleteLater()

    def _on_btn_clicked(self, text):
        if text == "C":
            self.current_expression = ""
            self.display.setText("")
        elif text == "=":
            self._evaluate_expression()
        else:
            self.current_expression += text
            self.display.setText(self.current_expression)

    def _evaluate_expression(self):
        try:
            if getattr(self, "converter_mode", False):
                value = float(self.current_expression)
                from_u = self.from_unit.currentText()
                to_u = self.to_unit.currentText()
                result = convert(value, from_u, to_u)
            else:
                result = eval(self.current_expression, {"__builtins__": None}, {})

            self.current_expression = str(round(result, 4))
            self.display.setText(self.current_expression)
        except Exception:
            self.display.setText("Error")
            self.current_expression = ""

    def keyPressEvent(self, event):
        key = event.key()
        allowed_keys = (
            list(range(Qt.Key_0, Qt.Key_9 + 1)) +
            [Qt.Key_Plus, Qt.Key_Minus, Qt.Key_Asterisk, Qt.Key_Slash, Qt.Key_Period]
        )

        if key in allowed_keys:
            self.current_expression += event.text()
        elif key in (Qt.Key_Enter, Qt.Key_Return):
            self._evaluate_expression()
            return
        elif key == Qt.Key_Backspace:
            self.current_expression = self.current_expression[:-1]
        elif key == Qt.Key_Escape:
            self.current_expression = ""
        else:
            return

        self.display.setText(self.current_expression)
