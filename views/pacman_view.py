import sys
import random
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QKeyEvent
from PySide6.QtCore import Qt, QTimer

CELL_SIZE = 30
GRID_WIDTH = 15
GRID_HEIGHT = 15

# 0 = empty, 1 = wall, 2 = dot
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,1,2,2,2,2,2,1,2,2,2,1],
    [1,2,1,2,1,2,1,1,1,2,1,2,1,2,1],
    [1,2,1,2,2,2,2,1,2,2,2,2,1,2,1],
    [1,2,1,1,1,1,2,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,0,1,1,2,1,1,1,1],
    [1,2,2,2,2,2,0,0,0,2,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,1,1,2,1,1,1,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,2,1,1,1,1,2,1],
    [1,2,1,2,2,2,2,1,2,2,2,2,1,2,1],
    [1,2,1,2,1,2,1,1,1,2,1,2,1,2,1],
    [1,2,2,2,1,2,2,2,2,2,1,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

class PacManGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pac-Man 2D")
        self.setFixedSize(GRID_WIDTH*CELL_SIZE, GRID_HEIGHT*CELL_SIZE)

        self.pacman_pos = [1, 1]  # Starting point
        self.pacman_dir = [0, 0]

        # Ghosts: starting positions
        self.ghosts = [
            [13, 1],
            [13, 13],
            [1, 13]
        ]

        self.score = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(200)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self.pacman_dir = [0, -1]
        elif event.key() == Qt.Key_Down:
            self.pacman_dir = [0, 1]
        elif event.key() == Qt.Key_Left:
            self.pacman_dir = [-1, 0]
        elif event.key() == Qt.Key_Right:
            self.pacman_dir = [1, 0]

    def game_loop(self):
        # Move Pac-Man
        new_x = self.pacman_pos[0] + self.pacman_dir[0]
        new_y = self.pacman_pos[1] + self.pacman_dir[1]
        if MAZE[new_y][new_x] != 1:
            self.pacman_pos = [new_x, new_y]

        # Eat dot
        if MAZE[new_y][new_x] == 2:
            MAZE[new_y][new_x] = 0
            self.score += 10

        # Move ghosts randomly
        for i, ghost in enumerate(self.ghosts):
            directions = [[0,1],[0,-1],[1,0],[-1,0]]
            random.shuffle(directions)
            for dx, dy in directions:
                gx, gy = ghost[0]+dx, ghost[1]+dy
                if MAZE[gy][gx] != 1:
                    self.ghosts[i] = [gx, gy]
                    break

        # Check collisions
        for ghost in self.ghosts:
            if ghost == self.pacman_pos:
                self.timer.stop()  # Game over

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw maze
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect_x, rect_y = x*CELL_SIZE, y*CELL_SIZE
                if MAZE[y][x] == 1:
                    painter.fillRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE, QColor("blue"))
                elif MAZE[y][x] == 2:
                    painter.setBrush(QColor("yellow"))
                    painter.drawEllipse(rect_x+CELL_SIZE//3, rect_y+CELL_SIZE//3, CELL_SIZE//3, CELL_SIZE//3)

        # Draw Pac-Man
        px, py = self.pacman_pos
        painter.setBrush(QColor("yellow"))
        painter.drawEllipse(px*CELL_SIZE, py*CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Draw ghosts
        painter.setBrush(QColor("red"))
        for gx, gy in self.ghosts:
            painter.drawEllipse(gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Draw score
        painter.setPen(QColor("white"))
        painter.drawText(10, 20, f"Score: {self.score}")

        # Game over message
        for ghost in self.ghosts:
            if ghost == self.pacman_pos and not self.timer.isActive():
                painter.drawText(self.width()//2 - 50, self.height()//2, "GAME OVER")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = PacManGame()
    game.show()
    sys.exit(app.exec())
