#!/usr/bin/env python
# НАЗВАНИЕ: Случайные пиксели
# ОПИСАНИЕ: Динамичная сетка из случайных цветных прямоугольников с плавной анимацией
# https://openprocessing.org/sketch/2682890
import time
import math
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw
from opensimplex import OpenSimplex
import numpy as np
import random



# -------------------------------------------------------------
# Конфигурация матрицы
# -------------------------------------------------------------
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# -------------------------------------------------------------
# Цвета и настройки
# -------------------------------------------------------------
COLORS = [
    "#f71735", "#f293af", "#fdb50e", "#2abde4", "#f4f0e6", "#2864b8"
]
BACKGROUND = "#272727"

WIDTH, HEIGHT = 64, 64
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2


# -------------------------------------------------------------
# Вспомогательные функции
# -------------------------------------------------------------
def ease_in_out_expo(x: float) -> float:
    if x == 0:
        return 0
    if x == 1:
        return 1
    if x < 0.5:
        return math.pow(2, 20 * x - 10) / 2
    return (2 - math.pow(2, -20 * x + 10)) / 2


def lerp(a, b, t):
    return a + (b - a) * t


# -------------------------------------------------------------
# Классы объектов
# -------------------------------------------------------------
class Shape:
    def __init__(self, x, y, w, h, clr, t):
        self.w0, self.w1 = 0, w
        self.h0, self.h1 = 0, h
        a = random.randint(0, 3) * (math.tau / 4)
        self.x0 = x + w * 3 * math.cos(a)
        self.y0 = y + h * 3 * math.sin(a)
        self.x1, self.y1 = x, y
        self.x, self.y = self.x0, self.y0
        self.w, self.h = self.w0, self.h0
        self.timer = t
        self.timings = [0, 20, 40, 60]
        self.exist = True
        self.clr = clr

    def update(self):
        self.timer += 1
        for i in range(len(self.timings) - 1):
            t1, t2 = self.timings[i], self.timings[i + 1]
            if t1 < self.timer < t2:
                n = (self.timer - t1) / (t2 - t1)
                if i == 0:
                    self.w = lerp(self.w0, self.w1, ease_in_out_expo(n))
                    self.h = lerp(self.h0, self.h1, ease_in_out_expo(n))
                elif i == 2:
                    self.x = lerp(self.x0, self.x1, ease_in_out_expo(n))
                    self.y = lerp(self.y0, self.y1, ease_in_out_expo(n))

    def draw(self, draw: ImageDraw.ImageDraw):
        if self.exist:
            x0 = self.x - self.w / 2
            y0 = self.y - self.h / 2
            x1 = self.x + self.w / 2
            y1 = self.y + self.h / 2
            draw.rectangle([x0, y0, x1, y1], fill=self.clr)


class MovingRect:
    def __init__(self, clr):
        self.clr = clr
        self.w = 0
        self.timer = 0
        self.span = 70

    def update(self):
        if 0 < self.timer < self.span:
            n = self.timer / (self.span - 1)
            self.w = lerp(0, WIDTH, ease_in_out_expo(n))
        self.timer += 1

    def draw(self, draw: ImageDraw.ImageDraw):
        half = self.w / 2
        draw.rectangle(
            [CENTER_X - half, CENTER_Y - half, CENTER_X + half, CENTER_Y + half],
            fill=self.clr
        )


# -------------------------------------------------------------
# Логика сцены
# -------------------------------------------------------------
shapes = []
rects = []
timer = 0


def initialize():
    global shapes, rects, timer
    shapes = []
    rects = []
    timer = 0
    random.shuffle(COLORS)
    cell_count = 6
    grid_area = WIDTH * 0.8
    cell_size = grid_area / cell_count
    offset = (WIDTH - grid_area) / 2

    for j in range(cell_count):
        for i in range(cell_count):
            x = i * cell_size + (cell_size / 2) + offset
            y = j * cell_size + (cell_size / 2) + offset
            form(x, y, cell_size * 0.75)


def form(x, y, w):
    cell_count = 4
    cell_size = w / cell_count
    for _ in range(6):
        num1 = random.randint(1, cell_count - 1)
        num2 = random.randint(1, cell_count - 1)
        ww = num1 * cell_size
        hh = num2 * cell_size
        xx = x - (w / 2) + (ww / 2) + random.randint(0, cell_count - num1) * cell_size
        yy = y - (w / 2) + (hh / 2) + random.randint(0, cell_count - num2) * cell_size
        clr = random.choice(COLORS)
        t = -random.randint(0, 140)
        shapes.append(Shape(xx, yy, ww, hh, clr, t))


# -------------------------------------------------------------
# Генерация одного кадра
# -------------------------------------------------------------
def generate_frame():
    global timer, rects
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(img)

    for s in shapes:
        s.update()
        s.draw(draw)
    for r in rects:
        r.update()
        r.draw(draw)

    # создание центрального прямоугольника
    start, span = 240, 5
    if start < timer <= (start + span):
        clr = COLORS[timer % len(COLORS)]
        if timer == (start + span):
            clr = BACKGROUND
        rects.append(MovingRect(clr))

    if timer == 300:
        initialize()

    timer += 1
    return img


# -------------------------------------------------------------
# Главный цикл
# -------------------------------------------------------------
if __name__ == "__main__":
    initialize()
    try:
        print("Press CTRL-C to stop.")
        while True:
            frame = generate_frame()
            matrix.SetImage(frame.convert("RGB"))
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nExiting...")
