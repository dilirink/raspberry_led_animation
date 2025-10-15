#!/usr/bin/env python
# НАЗВАНИЕ: Геометрия движения
# ОПИСАНИЕ: Анимированные геометрические фигуры с плавными трансформациями и цветовыми переходами
import time
import random
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw

import math


# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# Цвета из оригинального кода
colors = ['#f71735', '#067bc2', '#81cfe5', '#f654a9', '#2F0A30', '#f1d302']

def hex_to_rgb(hex_color):
    """Конвертация HEX в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def ease_in_out_cubic(x):
    """Функция плавности анимации"""
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2

def lerp(start, end, t):
    """Линейная интерполяция"""
    return start + (end - start) * t

def lerp_color(c1, c2, t):
    """Интерполяция цветов"""
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

class Motion:
    def __init__(self, x, y, w, clr1, clr2):
        self.x = x
        self.y = y
        self.w = w
        self.rest = 10
        self.t = -self.rest
        self.t1 = 50
        self.t2 = self.t1 + self.rest
        self.t3 = self.t2 + 50
        self.progress = 0
        self.clr1 = hex_to_rgb(clr1)
        self.clr2 = hex_to_rgb(clr2)
    
    def move(self):
        if 0 < self.t < self.t1:
            self.progress = ease_in_out_cubic(self.t / (self.t1 - 1))
        elif self.t2 < self.t < self.t3:
            self.progress = ease_in_out_cubic(1 - (self.t - self.t2) / (self.t3 - self.t2 - 1))
        elif (self.t3 + self.rest) < self.t:
            self.t = -self.rest
        self.t += 1
    
    def draw(self, draw_obj):
        pass

class Motion01(Motion):
    def draw(self, draw_obj):
        # Треугольник
        offset = self.w * self.progress
        points = [
            (self.x + self.w/2, self.y - self.w/2),
            (self.x + self.w/2 - offset, self.y + self.w/2 - offset),
            (self.x - self.w/2, self.y + self.w/2)
        ]
        draw_obj.polygon(points, fill=self.clr1)
        
        # Ромб с масштабированием
        scale_y = (self.progress * 2) - 1
        if abs(scale_y) > 0.01:
            diamond = [
                (self.x, self.y - self.w * 0.3 * scale_y),
                (self.x + self.w * 0.3, self.y),
                (self.x, self.y + self.w * 0.3 * scale_y),
                (self.x - self.w * 0.3, self.y)
            ]
            draw_obj.polygon(diamond, fill=self.clr2)

class Motion02(Motion):
    def draw(self, draw_obj):
        # Центральный круг
        r = self.w * (1 - self.progress) / 2
        draw_obj.ellipse([self.x - r, self.y - r, self.x + r, self.y + r], fill=self.clr2)
        
        # 5 маленьких кругов
        for i in range(5):
            angle = (i / 5) * 2 * math.pi + math.pi / 10
            radius = self.w * 0.4 * self.progress
            cx = self.x + radius * math.cos(angle)
            cy = self.y + radius * math.sin(angle)
            cr = self.w * 0.1 / 2
            draw_obj.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=self.clr2)
        
        # Звезда
        star_points = []
        for i in range(10):
            angle = (i / 10) * 2 * math.pi + math.pi / 10 + (1 - self.progress) * 2 * math.pi
            radius = lerp(0.25, 0.5, self.progress) * self.w
            if i % 2 == 0:
                radius *= 0.5
            star_points.append((
                self.x + radius * math.cos(angle),
                self.y + radius * math.sin(angle)
            ))
        draw_obj.polygon(star_points, fill=self.clr1)

class Motion03(Motion):
    def draw(self, draw_obj):
        # Левая дуга
        offset = self.w / 2 * (1 - self.progress)
        draw_obj.pieslice([self.x - offset - self.w/2, self.y - self.w/2, 
                          self.x - offset + self.w/2, self.y + self.w/2],
                         -90, 90, fill=self.clr1)
        
        # Правая дуга
        draw_obj.pieslice([self.x + offset - self.w/2, self.y - self.w/2,
                          self.x + offset + self.w/2, self.y + self.w/2],
                         90, 270, fill=self.clr1)
        
        # Центральный круг
        cr = self.w * 0.2 * self.progress / 2
        draw_obj.ellipse([self.x - cr, self.y - cr, self.x + cr, self.y + cr], fill=self.clr2)

class Motion04(Motion):
    def draw(self, draw_obj):
        # Дуга
        angle_range = lerp(0.1, 0.5, self.progress) * 180
        draw_obj.pieslice([self.x - self.w/2, self.y - self.w/2,
                          self.x + self.w/2, self.y + self.w/2],
                         90 - angle_range, 90 + angle_range, fill=self.clr1)
        
        # Движущийся круг
        cy = self.y + lerp(-self.w * 0.3, self.w * 0.3, self.progress)
        cr = self.w * 0.3 / 2
        clr = lerp_color(self.clr1, self.clr2, self.progress)
        draw_obj.ellipse([self.x - cr, cy - cr, self.x + cr, cy + cr], fill=clr)

# Инициализация анимаций
side = 64 * 0.8  # 51.2
graphic_size = side * 0.4  # ~20
motions = [
    Motion01(32 - side/4, 32 - side/4, graphic_size, colors[0], colors[1]),
    Motion02(32 + side/4, 32 - side/4, graphic_size, colors[2], colors[3]),
    Motion03(32 - side/4, 32 + side/4, graphic_size, colors[4], colors[5]),
    Motion04(32 + side/4, 32 + side/4, graphic_size, colors[1], colors[3])
]

def generate_frame():
    """Генерация одного кадра анимации"""
    img = Image.new('RGB', (64, 64), 'white')
    draw = ImageDraw.Draw(img)
    
    for motion in motions:
        motion.draw(draw)
        motion.move()
    
    return img

# Основной цикл анимации
try:
    print("Press CTRL-C to stop.")
    while True:
        frame = generate_frame()
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(0.02)  # ~30 FPS
except KeyboardInterrupt:
    print("Exiting...")