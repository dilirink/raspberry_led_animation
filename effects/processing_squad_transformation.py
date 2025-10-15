#!/usr/bin/env python
# НАЗВАНИЕ: Трансформация квадратов
# ОПИСАНИЕ: Рекурсивное деление прямоугольников с плавными переходами между состояниями
# https://openprocessing.org/sketch/1964607
import time
import math
import random
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw


# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# Глобальные переменные
WIDTH = 64
HEIGHT = 64
objs = []
colors = ['#DE183C', '#F2B541', '#0C79BB', '#ec4e20', '#00916e', '#f654a9']
arr1 = []
arr2 = []

# Вспомогательные функции
def hex_to_rgb(hex_color):
    """Конвертирует HEX в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def lerp(start, end, t):
    """Линейная интерполяция"""
    return start + (end - start) * t

def ease_in_out_quart(x):
    """Функция плавности"""
    return 8 * x * x * x * x if x < 0.5 else 1 - math.pow(-2 * x + 2, 4) / 2

def lerp_color(col1, col2, t):
    """Интерполяция цвета"""
    return tuple(int(lerp(col1[i], col2[i], t)) for i in range(3))

class Vector2:
    """Простой 2D вектор"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    @staticmethod
    def lerp(v1, v2, t):
        return Vector2(lerp(v1.x, v2.x, t), lerp(v1.y, v2.y, t))

def rec_rect(x, y, w, h, n, arr):
    """Рекурсивное разделение прямоугольников"""
    ww = random.uniform(0.1, 0.9) * w
    hh = random.uniform(0.1, 0.9) * h
    n -= 1
    
    if n >= 0:
        if w < h:
            rec_rect(x, y - (h / 2) + (hh / 2), w, hh, n, arr)
            rec_rect(x, y + (h / 2) - (h - hh) / 2, w, (h - hh), n, arr)
        else:
            rec_rect(x - (w / 2) + (ww / 2), y, ww, h, n, arr)
            rec_rect(x + (w / 2) - (w - ww) / 2, y, (w - ww), h, n, arr)
    else:
        arr.append({'x': x, 'y': y, 'w': w, 'h': h})

class Obj:
    """Класс анимированного объекта"""
    def __init__(self, pos1, w1, h1, pos2, w2, h2, t):
        self.pos1 = pos1
        self.pos2 = pos2
        self.pos = Vector2(self.pos1.x, self.pos1.y)
        self.w = w1
        self.h = h1
        self.w1 = w1
        self.h1 = h1
        self.w2 = w2
        self.h2 = h2
        self.t = -t
        self.t1 = 90
        self.t2 = self.t1 + 30
        self.t3 = self.t2 + 90
        self.t4 = self.t3 + 30
        self.cn = 0
        self.col1 = hex_to_rgb(colors[self.cn])
        self.col0 = (0, 0, 0)
        self.col = (0, 0, 0)
    
    def move(self):
        """Обновление позиции и цвета объекта"""
        if 0 < self.t < self.t1:
            n = (self.t) / (self.t1 - 1)
            ease_n = ease_in_out_quart(n)
            self.w = lerp(self.w1, self.w2, ease_n)
            self.h = lerp(self.h1, self.h2, ease_n)
            self.pos = Vector2.lerp(self.pos1, self.pos2, ease_n)
            self.col = lerp_color(self.col0, self.col1, math.sin(ease_n * math.pi))
        
        if self.t == self.t1:
            self.cn += 1
            self.col1 = hex_to_rgb(colors[self.cn % len(colors)])
        
        if self.t2 < self.t < self.t3:
            n = (self.t - self.t2) / (self.t3 - self.t2 - 1)
            ease_n = ease_in_out_quart(n)
            self.w = lerp(self.w2, self.w1, ease_n)
            self.h = lerp(self.h2, self.h1, ease_n)
            self.pos = Vector2.lerp(self.pos2, self.pos1, ease_n)
            self.col = lerp_color(self.col0, self.col1, math.sin(ease_n * math.pi))
        
        if self.t > self.t4:
            self.t = 0
            self.cn += 1
            self.col1 = hex_to_rgb(colors[self.cn % len(colors)])
        
        self.t += 1

def setup():
    """Инициализация анимации"""
    global objs, arr1, arr2
    num = 9
    rec_rect(WIDTH / 2, HEIGHT / 2, WIDTH * 0.9, HEIGHT * 0.9, num, arr1)
    rec_rect(WIDTH / 2, HEIGHT / 2, WIDTH * 0.6, HEIGHT * 0.6, num, arr2)
    
    for i in range(len(arr1)):
        s1 = arr1[i]
        s2 = arr2[i]
        pos1 = Vector2(s1['x'], s1['y'])
        pos2 = Vector2(s2['x'], s2['y'])
        dst = math.sqrt((WIDTH / 2 - pos1.x)**2 + (HEIGHT / 2 - pos1.y)**2)
        objs.append(Obj(pos1, s1['w'], s1['h'], pos2, s2['w'], s2['h'], int(dst / 10)))

def generate_frame():
    """Генерация одного кадра анимации"""
    image = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    for obj in objs:
        obj.move()
        x1 = obj.pos.x - obj.w / 2
        y1 = obj.pos.y - obj.h / 2
        x2 = obj.pos.x + obj.w / 2
        y2 = obj.pos.y + obj.h / 2
        draw.rectangle([x1, y1, x2, y2], fill=obj.col, outline=obj.col)
    
    return image

# Главный цикл
try:
    print("Инициализация...")
    setup()
    print("Запуск анимации. Нажмите CTRL-C для остановки.")
    
    while True:
        frame = generate_frame()
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(0.033)  # ~30 FPS
        
except KeyboardInterrupt:
    print("\nОстановка анимации...")
    matrix.Clear()
    print("Завершено.")