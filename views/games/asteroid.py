import math
import random
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QIcon, QPixmap

from utils.resource_path import resource_path

# Physics Enums
WIDTH, HEIGHT = 980, 680
FPS = 60
DT = 1 / FPS

ROT_SPEED = 3.0        # radians/sec
THRUST = 240.0         # pixels/sec²
DRAG = 0.99
MAX_SPEED = 420.0

BULLET_SPEED = 600.0
BULLET_LIFE = 1.0      # seconds

ASTEROID_MIN_SIZE = 20
ASTEROID_START_SIZE = 50


def wrap(pos: QPointF) -> QPointF:
    return QPointF(pos.x() % WIDTH, pos.y() % HEIGHT)

def vec_length(v: QPointF) -> float:
    return math.hypot(v.x(), v.y())

def limit(v: QPointF, max_len: float) -> QPointF:
    l = vec_length(v)
    if l > max_len:
        return v * (max_len / l)
    return v


@dataclass
class Bullet:
    pos: QPointF
    vel: QPointF
    life: float

    def update(self):
        self.pos += self.vel * DT
        self.pos = wrap(self.pos)
        self.life -= DT

@dataclass
class Asteroid:
    pos: QPointF
    vel: QPointF
    size: int
    shape: list
    color: QColor

    @staticmethod
    def spawn(size=ASTEROID_START_SIZE, pos=None):
        if pos is None:
            pos = QPointF(random.randrange(WIDTH), random.randrange(HEIGHT))

        angle = random.random() * math.tau
        speed = random.uniform(40, 120)
        vel = QPointF(math.cos(angle), math.sin(angle)) * speed

        shape = [
            QPointF(
                math.cos(a) * size * random.uniform(0.7, 1.2),
                math.sin(a) * size * random.uniform(0.7, 1.2)
            )
            for a in [i * math.tau / 8 for i in range(8)]
        ]

        color = QColor(
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255)
        )

        return Asteroid(pos, vel, size, shape, color)

    def update(self):
        self.pos += self.vel * DT
        self.pos = wrap(self.pos)

@dataclass
class Ship:
    pos: QPointF
    vel: QPointF
    angle: float
    hit_cooldown: float = 0.0

    def update(self, keys):

        if self.hit_cooldown > 0:
            self.hit_cooldown -= DT
        if Qt.Key.Key_Left in keys:
            self.angle -= ROT_SPEED * DT
        if Qt.Key.Key_Right in keys:
            self.angle += ROT_SPEED * DT

        if Qt.Key.Key_Up in keys:
            forward = QPointF(math.cos(self.angle), math.sin(self.angle))
            self.vel += forward * THRUST * DT

        self.vel *= DRAG
        self.vel = limit(self.vel, MAX_SPEED)
        self.pos += self.vel * DT
        self.pos = wrap(self.pos)

    def shoot(self):
        direction = QPointF(math.cos(self.angle), math.sin(self.angle))
        return Bullet(
            pos=QPointF(self.pos),
            vel=direction * BULLET_SPEED,
            life=BULLET_LIFE
        )

class AsteroidsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scratch Board: Asteroids")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(WIDTH, HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.ship = Ship(QPointF(WIDTH/2, HEIGHT/2), QPointF(), -math.pi/2)
        self.bullets: list[Bullet] = []
        self.asteroids = []
        while len(self.asteroids) < 6:
            a = Asteroid.spawn()
            if vec_length(a.pos - self.ship.pos) > 120:
                self.asteroids.append(a)

        self.keys = set()
        self.score = 0
        self.level = 1

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(int(1000 / FPS))

        self.game_running = False # Running flag for start/stop

        self.ship_image = QPixmap(
            resource_path("resources/icons/game_ship.png")
        )

        # Scale once for performance
        self.ship_image = self.ship_image.scaled(
            40, 40,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space:
            if not self.game_running:
                # Start the game if not running
                self.start_game()
            else:
                # Shoot bullet if game is running
                self.bullets.append(self.ship.shoot())
        elif e.key() == Qt.Key.Key_Escape:
            # Pause/unpause toggle
            if self.game_running:
                self.stop_game()
            else:
                self.start_game()
        else:
            self.keys.add(e.key())

    def keyReleaseEvent(self, e):
        self.keys.discard(e.key())

    def start_game(self):
        """Start or restart the game."""
        self.game_running = True
        self.ship = Ship(QPointF(WIDTH / 2, HEIGHT / 2), QPointF(), -math.pi / 2)
        self.bullets.clear()
        self.asteroids.clear()
        self.score = 0
        self.level = 1
        self.spawn_wave()
        self.timer.start(int(1000 / FPS))

    def stop_game(self):
        """Pause/stop the game."""
        self.game_running = False
        self.timer.stop()

    # Main game loop
    def update_game(self):
        if not self.game_running:
            return

        self.ship.update(self.keys)
        for b in self.bullets:
            b.update()
        for a in self.asteroids:
            a.update()

        self.handle_collisions()
        self.bullets = [b for b in self.bullets if b.life > 0]
        self.update()

        if not self.asteroids:
            self.level += 1
            self.spawn_wave()

    def spawn_wave(self):
        count = 6 + self.level * 3
        self.asteroids.clear()

        while len(self.asteroids) < count:
            a = Asteroid.spawn()
            if vec_length(a.pos - self.ship.pos) > 120:
                self.asteroids.append(a)

    # Detect collisions
    def handle_collisions(self):
        new_asteroids = []

        for b in self.bullets[:]:
            for a in self.asteroids[:]:
                if vec_length(b.pos - a.pos) < a.size:
                    self.bullets.remove(b)
                    self.asteroids.remove(a)
                    self.score += 10

                    if a.size > ASTEROID_MIN_SIZE:
                        for _ in range(2):
                            new_asteroids.append(
                                Asteroid.spawn(
                                    size=a.size // 2,
                                    pos=QPointF(a.pos)
                                )
                            )
                    break

        self.asteroids.extend(new_asteroids)

        for a in self.asteroids:
            if vec_length(self.ship.pos - a.pos) < a.size:
                if self.ship.hit_cooldown <= 0:
                    self.ship.vel = -self.ship.vel * 0.5
                    self.score -= 50
                    self.ship.hit_cooldown = 1.0  # 1 second invincibility
                break

    # Paint the event
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if not self.game_running:
            p.setPen(Qt.white)
            font = p.font()
            font.setPointSize(36)
            font.setBold(True)
            p.setFont(font)
            text = "Press SPACE to Begin/Restart\n\nPress ESC to stop"
            rect = self.rect()
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            return

        # Ship
        p.save()

        # Move origin to ship position
        p.translate(self.ship.pos)

        # Rotate (Qt uses degrees, 0° is along +X axis)
        p.rotate(math.degrees(self.ship.angle) + 90)

        # Draw centered
        w = self.ship_image.width()
        h = self.ship_image.height()
        p.drawPixmap(-w / 2, -h / 2, self.ship_image)

        p.restore()

        # Bullets
        p.setPen(QPen(QColor(255, 255, 0), 3))
        for b in self.bullets:
            p.drawPoint(b.pos)

        # Asteroids
        for a in self.asteroids:
            p.setPen(QPen(a.color, 1))
            p.drawPolygon([a.pos + pt for pt in a.shape])

        # Score
        p.setPen(Qt.white)

        # Set a larger font
        font = p.font()  # get current font
        font.setPointSize(24)  # increase font size
        font.setBold(True)
        p.setFont(font)

        p.drawText(10, 25, f"SCORE {self.score}")


if __name__ == "__main__":
    app = QApplication([])
    w = AsteroidsWidget()
    w.show()
    app.exec()
