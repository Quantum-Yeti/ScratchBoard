import math
import secrets
import string

from PySide6.QtGui import QIcon, Qt, QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QWidget, QHBoxLayout, QSpinBox, QCheckBox, \
    QLineEdit, QProgressBar, QPushButton, QApplication, QSizePolicy, QStackedWidget

from utils.custom_context_menu import ContextMenuUtility
from utils.resource_path import resource_path


def load_wordlist():
    path = resource_path("resources/wordlist.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip() for w in f.readlines() if w.strip()]
    except Exception:
        return ["apple", "banana", "cloud", "river", "metal", "storm"]


class PassGenWidget(QDialog):
    """
    QDialog widget for generating passwords.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Window setup
        self.setWindowTitle("Scratch Board: Password Generator")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedHeight(500)
        self.setMinimumWidth(420)
        self.setFont(QFont("Segoe UI", 11))

        # Layout of the window
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Modes
        self.select_mode = QComboBox()
        self.select_mode.addItems(["Quick Mode [word+number]", "Quick Mode [char]", "Advanced Mode [words]"])
        self.select_mode.currentIndexChanged.connect(self.update_visibility)

        # Mode selection
        layout.addWidget(QLabel("Select Mode:"))
        layout.addWidget(self.select_mode)

        # Setup of quick word+number option
        quick_layout = QHBoxLayout()
        self.quick_widget = QWidget()
        self.quick_widget.setLayout(quick_layout)

        # Setup of quick char option
        char_layout = QVBoxLayout()
        self.char_widget = QWidget()
        self.char_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.char_widget.setContentsMargins(0, 0, 0, 0)
        self.char_widget.setMinimumHeight(0)
        self.char_widget.setLayout(char_layout)

        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(8, 64)
        self.length_spinbox.setValue(16)
        length_layout.addWidget(self.length_spinbox)

        char_layout.addLayout(length_layout)

        self.upper_char = QCheckBox("Uppercase (A-Z")
        self.upper_char.setChecked(False)

        self.include_num = QCheckBox("Numbers (0-9)")
        self.include_num.setChecked(False)

        self.include_special_char = QCheckBox("Symbols (!@#")
        self.include_special_char.setChecked(False)

        char_layout.addWidget(self.upper_char)
        char_layout.addWidget(self.include_num)
        char_layout.addWidget(self.include_special_char)

        # Setup of random words option
        self.words = QWidget()
        self.words.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.words.setMinimumHeight(0)
        self.words.setContentsMargins(0, 0, 0, 0)
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
        self.separator_box.setCurrentText("none")
        sep_layout.addWidget(self.separator_box)
        word_layout.addLayout(sep_layout)

        word_layout.addWidget(self.add_nums)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.char_widget)  # index 0 = Quick char mode
        self.stack.addWidget(self.words)  # index 1 = Advanced mode
        self.stack.addWidget(self.quick_widget) # index 2 = very quick mode
        layout.addWidget(self.stack)

        #layout.addWidget(self.words)

        # Generated password output
        self.output = QLineEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.context_menu_helper = ContextMenuUtility(self.output)

        # Strength + entropy
        self.strength_label = QLabel("Strength: ---")
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.strength_label)

        self.entropy_bar = QProgressBar()
        self.entropy_bar.setRange(0, 100)
        layout.addWidget(self.entropy_bar)

        # Setup generate and copy buttons
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setIcon(QIcon(resource_path("resources/icons/polybase.png")))
        self.generate_btn.clicked.connect(self.generate)

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setIcon(QIcon(resource_path("resources/icons/copy.png")))
        self.copy_btn.clicked.connect(self.copy_password)

        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.copy_btn)

        # Add buttons to layout
        layout.addLayout(btn_layout)

        # Add the layout initialization to layout
        self.setLayout(layout)

        # Prepare wordlist
        self.wordlist = load_wordlist()

        self.update_visibility()

        # Styling
        style_path = resource_path("ui/themes/passgen_theme.qss")
        with open(style_path, "r") as f:
            self.setStyleSheet(f.read())

    def update_visibility(self):
        mode = self.select_mode.currentText()
        if mode == "Quick Mode [char]":
            self.stack.setCurrentIndex(0)
        elif mode == "Quick Mode [word+number]":
            self.stack.setCurrentIndex(2)
        else:
            self.stack.setCurrentIndex(1)

    def generate(self):
        mode = self.select_mode.currentText()

        if mode == "Quick Mode [char]":
            password = self.generate_char_password()
        elif mode == "Quick Mode [word+number]":
            password = self.generate_word_number_password()
        else:
            password = self.generate_word_password()

        self.output.setText(password)
        QApplication.clipboard().setText(password)

    def generate_word_number_password(self):
        # Choose a random word from the wordlist
        word = secrets.choice(self.wordlist)

        # Choose a random number between 0 and 99
        number = secrets.randbelow(100)

        # Optionally capitalize the word
        if self.caps_words.isChecked():
            word = word.capitalize()

        # Combine the word and number
        password = f"{word}{number}"

        # Update the strength bar based on the entropy (log2 of wordlist size * number of words)
        entropy = math.log2(len(self.wordlist)) + math.log2(100)  # Adding log2(100) for the number range
        self.update_strength_from_entropy(entropy)

        return password

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
            charset += "!@#-_"
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