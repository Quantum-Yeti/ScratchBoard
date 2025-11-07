# views/pacman_view.py
import sys

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QFont
import random

CELL_SIZE = 30

class PacmanView(QWidget):
    """A simple Pac-Man game with ghosts, walls, pellets, and scoring."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(19 * CELL_SIZE, 15 * CELL_SIZE)
        self.setFocusPolicy(Qt.StrongFocus)

        # Maze layout: 0=empty, 1=wall, 2=pellet
        self.maze_layout = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,2,2,2,1,2,2,2,2,1,2,2,2,2,1,2,2,2,1],
            [1,2,1,2,1,2,1,1,2,1,2,1,1,2,1,2,1,2,1],
            [1,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,1],
            [1,2,1,2,1,1,1,0,1,1,1,0,1,1,1,2,1,2,1],
            [1,2,2,2,1,2,2,2,2,1,2,2,2,2,1,2,2,2,1],
            [1,1,1,2,1,2,1,1,2,1,2,1,1,2,1,2,1,1,1],
            [1,2,2,2,2,2,2,0,2,2,2,0,2,2,2,2,2,2,1],
            [1,2,1,1,1,2,1,1,2,1,2,1,1,2,1,1,1,2,1],
            [1,2,2,2,2,2,2,2,2,0,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,1,2,1,1,2,1,2,1,1,2,1,1,1,2,1],
            [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]

        # Player
        self.player_x, self.player_y = 1, 1
        self.player_dx, self.player_dy = 0, 0

        # Ghosts
        self.ghosts = [
            {"x": 9, "y": 7, "color": "red", "dx": 0, "dy": -1},
            {"x": 9, "y": 8, "color": "pink", "dx": 0, "dy": 1},
        ]

        self.score = 0
        self.game_over = False

        # Timer for game loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(200)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw maze
        for y, row in enumerate(self.maze_layout):
            for x, cell in enumerate(row):
                if cell == 1:
                    painter.setBrush(QBrush(QColor("blue")))
                    painter.drawRect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                elif cell == 2:
                    painter.setBrush(QBrush(QColor("yellow")))
                    radius = CELL_SIZE // 6
                    painter.drawEllipse(
                        x*CELL_SIZE + CELL_SIZE//2 - radius,
                        y*CELL_SIZE + CELL_SIZE//2 - radius,
                        radius*2, radius*2
                    )

        # Draw player
        painter.setBrush(QBrush(QColor("orange")))
        painter.drawEllipse(
            self.player_x*CELL_SIZE,
            self.player_y*CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )

        # Draw ghosts
        for ghost in self.ghosts:
            painter.setBrush(QBrush(QColor(ghost["color"])))
            painter.drawEllipse(
                ghost["x"]*CELL_SIZE,
                ghost["y"]*CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )

        # Draw score
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(5, 15, f"Score: {self.score}")

        # Game over
        if self.game_over:
            painter.setFont(QFont("Arial", 24, QFont.Bold))
            painter.setPen(QColor("red"))
            painter.drawText(self.width()//4, self.height()//2, "GAME OVER")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.player_dx, self.player_dy = -1, 0
        elif key == Qt.Key_Right:
            self.player_dx, self.player_dy = 1, 0
        elif key == Qt.Key_Up:
            self.player_dx, self.player_dy = 0, -1
        elif key == Qt.Key_Down:
            self.player_dx, self.player_dy = 0, 1

    def game_loop(self):
        if self.game_over:
            self.timer.stop()
            return

        # Move player
        new_x = self.player_x + self.player_dx
        new_y = self.player_y + self.player_dy
        if self.can_move(new_x, new_y):
            self.player_x, self.player_y = new_x, new_y

        # Eat pellet
        if self.maze_layout[self.player_y][self.player_x] == 2:
            self.maze_layout[self.player_y][self.player_x] = 0
            self.score += 10

        # Move ghosts
        for ghost in self.ghosts:
            self.move_ghost(ghost)

        # Check collisions
        for ghost in self.ghosts:
            if ghost["x"] == self.player_x and ghost["y"] == self.player_y:
                self.game_over = True

        self.update()

    def can_move(self, x, y):
        if 0 <= y < len(self.maze_layout) and 0 <= x < len(self.maze_layout[0]):
            return self.maze_layout[y][x] != 1
        return False

    def move_ghost(self, ghost):
        # Simple random movement
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = ghost["x"] + dx
            new_y = ghost["y"] + dy
            if self.can_move(new_x, new_y):
                ghost["x"], ghost["y"] = new_x, new_y
                break
def main():
    app = QApplication(sys.argv)

    # Create and show the Pac-Man game window
    game_window = PacmanView()
    game_window.show()

    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()