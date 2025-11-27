import math
import secrets
import string

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QWidget, QHBoxLayout, QSpinBox, QCheckBox, \
    QLineEdit, QProgressBar, QPushButton, QApplication

from utils.resource_path import resource_path

class PassGenWidget(QDialog):
    """
    QDialog widget for generating passwords.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Scratch Board: Password Generator")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setMinimumWidth(420)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.select_mode = QComboBox()
        self.select_mode.addItems(["Quick", "Advanced"])
        self.select_mode.currentIndexChanged.connect(self.update_visibility)

        layout.addWidget(QLabel("Select Mode:"))
        layout.addWidget(self.select_mode)

        char_layout = QVBoxLayout()
        self.char_widget = QWidget()
        self.char_widget.setLayout(char_layout)

        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(8, 64)
        self.length_spinbox.setValue(16)
        length_layout.addWidget(self.length_spinbox)

        char_layout.addLayout(length_layout)

        self.upper_char = QCheckBox("Uppercase (A-Z")
        self.upper_char.setChecked(True)

        self.include_num = QCheckBox("Numbers (0-9)")
        self.include_num.setChecked(True)

        self.include_special_char = QCheckBox("Symbols (!@#")
        self.include_special_char.setChecked(True)

        char_layout.addWidget(self.upper_char)
        char_layout.addWidget(self.include_num)
        char_layout.addWidget(self.include_special_char)

        layout.addWidget(self.char_widget)

        self.words = QWidget()
        word_layout = QVBoxLayout()
        self.words.setLayout(word_layout)

        word_count_layout = QHBoxLayout()
        word_count_layout.addWidget(QLabel("Words:"))
        self.word_spinbox = QSpinBox()
        self.word_spinbox.setRange(2, 12)
        self.word_spinbox.setValue(2)
        word_count_layout.addWidget(self.word_spinbox)
        word_layout.addLayout(word_count_layout)

        self.caps_words = QCheckBox("Capitalization")
        self.add_nums = QCheckBox("Numbers (+)")
        self.caps_words.setChecked(False)

        word_layout.addWidget(self.caps_words)

        # Separator selector
        sep_layout = QHBoxLayout()
        sep_layout.addWidget(QLabel("Separator:"))
        self.separator_box = QComboBox()
        self.separator_box.addItems(["-", "_", "space", "none"])
        sep_layout.addWidget(self.separator_box)
        word_layout.addLayout(sep_layout)

        word_layout.addWidget(self.add_nums)

        layout.addWidget(self.words)

        self.output = QLineEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.strength_label = QLabel("Strength: ---")
        self.strength_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.strength_label)

        self.entropy_bar = QProgressBar()
        self.entropy_bar.setRange(0, 100)
        layout.addWidget(self.entropy_bar)

        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setIcon(QIcon(resource_path("resources/icons/refresh.png")))
        self.generate_btn.clicked.connect(self.generate)

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setIcon(QIcon(resource_path("resources/icons/copy.png")))
        self.copy_btn.clicked.connect(self.copy_password)

        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.copy_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.wordlist = self.load_wordlist()

        self.update_visibility()

    def update_visibility(self):
        mode = self.select_mode.currentText()
        self.char_widget.setVisible(mode == "Quick")
        self.words.setVisible(mode == "Advanced")

    def load_wordlist(self):
        path = resource_path("resources/wordlist.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [w.strip() for w in f.readlines() if w.strip()]
        except Exception:
            return ["apple", "banana", "cloud", "river", "metal", "storm"]

    def generate(self):
        mode = self.select_mode.currentText()

        if mode == "Quick":
            password = self.generate_char_password()
        else:
            password = self.generate_word_password()

        self.output.setText(password)
        QApplication.clipboard().setText(password)

    def generate_char_password(self):
        charset = string.ascii_lowercase
        pool = 26

        if self.upper_char.isChecked():
            charset += string.ascii_uppercase
            pool += 26
        if self.include_num.isChecked():
            charset += string.digits
            pool += 10
        if self.include_special_char.isChecked():
            charset += "!@#$%^&*()-_=+[]{}<>/?"
            pool += 30

        length = self.length_spinbox.value()
        pw = "".join(secrets.choice(charset) for _ in range(length))

        self.update_strength(pool, length)
        return pw

    def generate_word_password(self):
        n = self.word_spinbox.value()
        words = [secrets.choice(self.wordlist) for _ in range(n)]

        if self.caps_words.isChecked():
            words = [w.capitalize() for w in words]

        sep = self.separator_box.currentText()
        if sep == "space":
            sep_char = " "
        elif sep == "none":
            sep_char = ""
        else:
            sep_char = sep

        pw = sep_char.join(words)

        if self.add_nums.isChecked():
            pw += str(secrets.randbelow(100))

        # entropy ≈ log2(wordlist_size^words)
        entropy = n * math.log2(len(self.wordlist))
        self.update_strength_from_entropy(entropy)

        return pw

    def copy_password(self):
        QApplication.clipboard().setText(self.output.text())

    def update_strength(self, pool_size, length):
        entropy = length * math.log2(pool_size)
        self.update_strength_from_entropy(entropy)

    def update_strength_from_entropy(self, entropy):
        self.entropy_bar.setValue(min(int(entropy), 100))
        self.entropy_bar.setFormat(f"Entropy: {int(entropy)} bits")

        if entropy < 40:
            txt, col = "Weak", "#d9534f"
        elif entropy < 70:
            txt, col = "Medium", "#f0ad4e"
        elif entropy < 100:
            txt, col = "Strong", "#5cb85c"
        else:
            txt, col = "Very Strong", "#4CAF50"

        self.strength_label.setText(f"Strength: {txt}")
        self.strength_label.setStyleSheet(f"color: {col}; font-weight: bold;")