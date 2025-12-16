import math
import random
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QIcon

from utils.resource_path import resource_path

# ---------- Physics tuning ----------
ROT_SPEED = 0.045
THRUST = 0.09
DRAG = 0.985
MAX_SPEED = 4.5


def wrap(pos, w, h):
    return QPointF(pos.x() % w, pos.y() % h)


class Asteroid:
    def __init__(self, w, h, size=40):
        self.pos = QPointF(random.randint(0, w), random.randint(0, h))
        angle = random.random() * 2 * math.pi
        speed = random.uniform(0.5, 1.5)
        self.vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
        self.size = size
        self.shape = [
            QPointF(
                math.cos(a) * size * random.uniform(0.7, 1.2),
                math.sin(a) * size * random.uniform(0.7, 1.2),
            )
            for a in [i * 2 * math.pi / 8 for i in range(8)]
        ]

        # Asteroid colors
        self.color = QColor(
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

    def update(self, w, h):
        self.pos += self.vel
        self.pos = wrap(self.pos, w, h)


class Bullet:
    def __init__(self, pos, angle):
        self.pos = QPointF(pos)
        self.vel = QPointF(math.cos(angle) * 6, math.sin(angle) * 6)
        self.life = 60

    def update(self, w, h):
        self.pos += self.vel
        self.pos = wrap(self.pos, w, h)
        self.life -= 1


class AsteroidsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scratch Board: Asteroids")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.w, self.h = 980, 680
        self.setFixedSize(self.w, self.h)

        # Ship
        self.ship_pos = QPointF(self.w / 2, self.h / 2)
        self.ship_vel = QPointF(0, 0)
        self.ship_angle = -math.pi / 2
        self._ship_got_hit = False

        self.bullets = []

        self.asteroids = []
        for _ in range(6):
            while True:
                a = Asteroid(self.w, self.h)
                delta = a.pos - self.ship_pos
                if math.hypot(delta.x(), delta.y()) > 60:  # safe distance from ship
                    self.asteroids.append(a)
                    break

        self.keys = set()
        self.score = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

    # Keyboard Input
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Space:
            self.bullets.append(Bullet(self.ship_pos, self.ship_angle))
        elif e.key() == Qt.Key_Escape:
            self.close()
        else:
            self.keys.add(e.key())

    def keyReleaseEvent(self, e):
        self.keys.discard(e.key())

    def mousePressEvent(self, e):
        self.bullets.append(Bullet(self.ship_pos, self.ship_angle))

    # Main Loop
    def update_game(self):
        # Rotation
        if Qt.Key_Left in self.keys:
            self.ship_angle -= ROT_SPEED
        if Qt.Key_Right in self.keys:
            self.ship_angle += ROT_SPEED

        # Thrust
        if Qt.Key_Up in self.keys:
            thrust = QPointF(
                math.cos(self.ship_angle),
                math.sin(self.ship_angle)
            ) * THRUST
            self.ship_vel += thrust

        # Velocity max
        speed = self.ship_vel.manhattanLength()
        if speed > MAX_SPEED:
            self.ship_vel *= MAX_SPEED / speed

        # Movement + drag
        self.ship_pos += self.ship_vel
        self.ship_vel *= DRAG
        self.ship_pos = wrap(self.ship_pos, self.w, self.h)

        # Bullets
        for b in self.bullets[:]:
            b.update(self.w, self.h)
            if b.life <= 0:
                self.bullets.remove(b)

        # Asteroids
        for a in self.asteroids:
            a.update(self.w, self.h)

        self.check_collisions()
        self.check_ship_collision()
        self.update()

    # Detect collisions
    def check_collisions(self):
        for b in self.bullets[:]:
            for a in self.asteroids[:]:
                delta = b.pos - a.pos
                dist = math.hypot(delta.x(), delta.y())
                if dist < a.size:
                    self.bullets.remove(b)
                    self.asteroids.remove(a)
                    self.score += 10

                    if a.size > 20:
                        self.asteroids.append(Asteroid(self.w, self.h, a.size // 2))
                        self.asteroids.append(Asteroid(self.w, self.h, a.size // 2))
                    break

    # Paint the event
    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0))
        p.setPen(QPen(Qt.white, 1))

        # Ship
        ship_shape = [
            QPointF(20, 0),
            QPointF(-16, 6),
            QPointF(-10, 0),
            QPointF(-16, -6),
        ]
        ship = []
        for pt in ship_shape:
            x = pt.x() * math.cos(self.ship_angle) - pt.y() * math.sin(self.ship_angle)
            y = pt.x() * math.sin(self.ship_angle) + pt.y() * math.cos(self.ship_angle)
            ship.append(self.ship_pos + QPointF(x, y))
        p.drawPolygon(ship)

        # Bullets
        for b in self.bullets:
            p.drawPoint(b.pos)

        # Asteroids
        for a in self.asteroids:
            p.setPen(QPen(a.color, 1))
            poly = [a.pos + pt for pt in a.shape]
            p.drawPolygon(poly)

        # Score
        font = p.font()
        font.setPointSize(20)
        p.setFont(font)
        p.drawText(10, 20, f"SCORE {self.score}")

    def check_ship_collision(self):
        hit = False
        for a in self.asteroids:
            delta = self.ship_pos - a.pos
            dist = math.hypot(delta.x(), delta.y())
            if dist < a.size:
                hit = True
                self.ship_vel = -self.ship_vel * 1.5

        if hit and not self._ship_got_hit:
            self.score -= 10
        self._ship_got_hit = hit


if __name__ == "__main__":
    app = QApplication([])
    w = AsteroidsWidget()
    w.show()
    app.exec()
