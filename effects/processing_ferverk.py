#!/usr/bin/env python
# НАЗВАНИЕ: Фейерверк
# ОПИСАНИЕ: Красочный анимированный фейерверк с частицами и искрами
# https://openprocessing.org/sketch/2326097
#!/usr/bin/env python3
import time
import random
import math
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw

# -------------------------------------------------------------
# Конфигурация для LED-матрицы 64x64
# -------------------------------------------------------------
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'  # для эмулятора
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# -------------------------------------------------------------
# Цвета и утилиты
# -------------------------------------------------------------
COLORS = [(237, 52, 65), (255, 214, 48), (50, 159, 227),
          (8, 172, 126), (222, 217, 223), (254, 77, 3)]


def ease_out_circ(x):
    return math.sqrt(1 - (x - 1) ** 2)


# -------------------------------------------------------------
# Классы объектов
# -------------------------------------------------------------
class Orb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 5
        self.r_step = random.uniform(0.3, 1.0)
        self.max_circle_d = 1.5
        self.circle_d = 1.5
        self.is_dead = False
        self.ang = random.random() * math.pi * 2
        self.ang_step = random.choice([-1, 1]) * random.uniform(0.05, 0.3)
        self.x_step = random.choice([-1, 1]) * random.uniform(0.05, 0.2)
        self.y_step = random.choice([-1, 1]) * random.uniform(0.05, 0.2)
        self.life = 0
        self.life_span = random.randint(20, 80)
        self.col = random.choice(COLORS)
        self.pos = [(x, y)]
        self.followers = 5

    def move(self):
        self.ang += self.ang_step
        self.x += self.x_step
        self.y += self.y_step
        self.radius = min(self.radius + self.r_step, self.max_radius)
        self.life += 1
        if self.life > self.life_span:
            self.is_dead = True

        xx = self.x + self.radius * math.cos(self.ang)
        yy = self.y + self.radius * math.sin(self.ang)
        self.pos.append((xx, yy))
        if len(self.pos) > self.followers:
            self.pos.pop(0)

    def draw(self, draw):
        if len(self.pos) > 1:
            draw.line(self.pos, fill=self.col, width=int(self.circle_d))


class Sparkle:
    def __init__(self, x, y):
        self.x0 = x
        self.y0 = y
        self.r = random.uniform(5, 30)
        self.a = random.random() * math.pi * 2
        self.x = x
        self.y = y
        self.target_x = x + self.r * math.cos(self.a)
        self.target_y = y + self.r * math.sin(self.a)
        self.life = 0
        self.life_span = random.randint(30, 100)
        self.col = random.choice(COLORS)
        self.is_dead = False

    def move(self):
        nrm = self.life / self.life_span
        nrm = min(max(nrm, 0), 1)
        self.x = self.x0 + (self.target_x - self.x0) * ease_out_circ(nrm)
        self.y = self.y0 + (self.target_y - self.y0) * ease_out_circ(nrm)
        self.life += 1
        if self.life > self.life_span:
            self.is_dead = True

    def draw(self, draw):
        draw.point((self.x, self.y), fill=self.col)


class Ripple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 0
        self.life_span = random.randint(30, 80)
        self.col = random.choice(COLORS)
        self.max_d = random.uniform(10, 25)
        self.is_dead = False

    def move(self):
        self.life += 1
        if self.life > self.life_span:
            self.is_dead = True
        self.d = self.max_d * ease_out_circ(self.life / self.life_span)

    def draw(self, draw):
        r = self.d / 2
        bbox = [self.x - r, self.y - r, self.x + r, self.y + r]
        draw.ellipse(bbox, outline=self.col)


class Shape:
    def __init__(self, x, y):
        self.x0 = x
        self.y0 = y
        self.life = 0
        self.life_span = random.randint(30, 100)
        self.col = random.choice(COLORS)
        self.size = random.uniform(3, 10)
        self.ang = random.random() * math.pi * 2
        self.ang_step = random.choice([-1, 1]) * random.uniform(0.02, 0.1)
        self.shape_type = random.randint(0, 2)
        self.r = random.uniform(5, 25)
        self.a = random.random() * math.pi * 2
        self.target_x = x + self.r * math.cos(self.a)
        self.target_y = y + self.r * math.sin(self.a)
        self.is_dead = False

    def move(self):
        self.life += 1
        if self.life > self.life_span:
            self.is_dead = True
        nrm = ease_out_circ(self.life / self.life_span)
        self.x = self.x0 + (self.target_x - self.x0) * nrm
        self.y = self.y0 + (self.target_y - self.y0) * nrm
        self.ang += self.ang_step

    def draw(self, draw):
        if self.shape_type == 0:
            draw.rectangle([self.x - self.size, self.y - self.size,
                            self.x + self.size, self.y + self.size],
                           outline=self.col)
        elif self.shape_type == 1:
            r = self.size
            draw.ellipse([self.x - r, self.y - r, self.x + r, self.y + r],
                         outline=self.col)
        else:
            draw.line([self.x - self.size, self.y,
                       self.x + self.size, self.y], fill=self.col)
            draw.line([self.x, self.y - self.size,
                       self.x, self.y + self.size], fill=self.col)


# -------------------------------------------------------------
# Управление объектами
# -------------------------------------------------------------
objects = []


def add_objs():
    x = random.uniform(0, 64)
    y = random.uniform(0, 64)
    for _ in range(5):
        objects.append(Orb(x, y))
    for _ in range(10):
        objects.append(Sparkle(x, y))
    for _ in range(2):
        objects.append(Ripple(x, y))
    for _ in range(4):
        objects.append(Shape(x, y))


# -------------------------------------------------------------
# Основной цикл анимации
# -------------------------------------------------------------
try:
    print("Запуск анимации. Нажмите CTRL+C для выхода.")
    frame_count = 0
    while True:
        img = Image.new("RGB", (64, 64), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        for obj in list(objects):
            obj.move()
            obj.draw(draw)
            if getattr(obj, "is_dead", False):
                objects.remove(obj)

        # случайное добавление новых объектов
        if frame_count % random.choice([10, 30, 60]) == 0:
            add_objs()

        matrix.SetImage(img)
        frame_count += 1
        time.sleep(0.05)  # скорость кадров (~20 FPS)

except KeyboardInterrupt:
    print("Выход...")