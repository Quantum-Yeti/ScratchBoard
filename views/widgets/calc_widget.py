from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QGridLayout, QPushButton, QLabel, QSizePolicy

from utils.resource_path import resource_path


class SimpleCalcView(QDialog):
    """
    Minimal calculator with normal mode and outage mode.
    Outage Mode: calculate cost of service downtime based on monthly charge.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: Simple Calculator/Outage Calculator")
        self.setFixedSize(400, 500)

        self.current_expression = ""
        self.outage_mode = False

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
        self.mode_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mode_button.setFixedHeight(50)
        self.mode_button.toggled.connect(self._toggle_outage_mode)
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
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

    def _toggle_outage_mode(self, checked):
        self.outage_mode = checked
        self.display.setText("")
        self.current_expression = ""
        self.mode_button.setText("Outage Mode" if checked else "Normal Mode")
        self.display.setPlaceholderText("Monthly fee / hours offline" if checked else "")

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
            if self.outage_mode:
                parts = self.current_expression.split('/')
                if len(parts) != 2:
                    self.display.setText("Error")
                    return
                monthly_charge = float(parts[0].strip())
                hours_offline = float(parts[1].strip())
                result = monthly_charge * (hours_offline / (30*24))  # proportional cost
            else:
                result = eval(self.current_expression, {"__builtins__": None}, {})

            self.current_expression = str(round(result, 2))
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
