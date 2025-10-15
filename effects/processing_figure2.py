#!/usr/bin/env python
# НАЗВАНИЕ: Геометрия 2
# ОПИСАНИЕ: Продвинутые геометрические паттерны с вращением, движением и трансформацией
# https://openprocessing.org/sketch/2494961
import time
import math
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
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

# Новые цвета
colors = ['#083d77', '#da4167', '#ffd639', '#81cfe5', '#FBAF00', '#00AF54']

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
    """Крест с квадратом"""
    def draw(self, draw_obj):
        # Вертикальный прямоугольник
        rect_h = self.w / 2
        rect_y = (self.w / 4) - (self.progress * self.w / 2)
        draw_obj.rectangle([
            self.x - self.w/2, self.y + rect_y - rect_h/2,
            self.x + self.w/2, self.y + rect_y + rect_h/2
        ], fill=self.clr1)
        
        # Горизонтальный прямоугольник
        rect_w = self.w / 2
        rect_x = (self.w / 4) - (self.progress * self.w / 2)
        draw_obj.rectangle([
            self.x + rect_x - rect_w/2, self.y - self.w/2,
            self.x + rect_x + rect_w/2, self.y + self.w/2
        ], fill=self.clr2)
        
        # Квадрат со скруглением
        sq_size = self.w * lerp(0.25, 0.5, self.progress)
        corner_radius = self.w / 2 * (1 - self.progress)
        draw_obj.rounded_rectangle([
            self.x + self.w/4 - sq_size/2, self.y + self.w/4 - sq_size/2,
            self.x + self.w/4 + sq_size/2, self.y + self.w/4 + sq_size/2
        ], radius=corner_radius, fill=self.clr1)

class Motion02(Motion):
    """Вращающиеся квадраты"""
    def draw(self, draw_obj):
        # Центральный вращающийся квадрат
        angle = math.pi * (1 - self.progress)
        sq_size = self.w / 3
        
        # Поворот квадрата вокруг центра
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        half = sq_size / 2
        
        corners = [
            (-half, -half), (half, -half), (half, half), (-half, half)
        ]
        rotated = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + self.x
            ry = cx * sin_a + cy * cos_a + self.y
            rotated.append((rx, ry))
        
        draw_obj.polygon(rotated, fill=self.clr1)
        
        # Верхний правый квадрат (движется вверх)
        sq_y1 = (self.w / 3) - (self.w / 3 * 2 * self.progress)
        draw_obj.rectangle([
            self.x + self.w/3 - sq_size/2, self.y + sq_y1 - sq_size/2,
            self.x + self.w/3 + sq_size/2, self.y + sq_y1 + sq_size/2
        ], fill=self.clr2)
        
        # Нижний левый квадрат (движется вниз)
        sq_y2 = -(self.w / 3) + (self.w / 3 * 2 * self.progress)
        draw_obj.rectangle([
            self.x - self.w/3 - sq_size/2, self.y + sq_y2 - sq_size/2,
            self.x - self.w/3 + sq_size/2, self.y + sq_y2 + sq_size/2
        ], fill=self.clr2)

class Motion03(Motion):
    """Движущиеся треугольники"""
    def draw(self, draw_obj):
        offset = self.w / 2 * self.progress
        
        # Верхний треугольник (основной)
        triangle1 = [
            (self.x, self.y - self.w/2 + offset),
            (self.x + self.w/2, self.y - self.w/4 + offset),
            (self.x, self.y + offset),
            (self.x - self.w/2, self.y - self.w/4 + offset)
        ]
        draw_obj.polygon(triangle1, fill=self.clr1)
        
        # Нижний треугольник
        triangle2 = [
            (self.x + self.w/2, self.y - self.w/4 + offset),
            (self.x, self.y + offset),
            (self.x - self.w/2, self.y - self.w/4 + offset),
            (self.x - self.w/2, self.y - self.w/4 + self.w/2),
            (self.x, self.y + self.w/2),
            (self.x + self.w/2, self.y - self.w/4 + self.w/2)
        ]
        draw_obj.polygon(triangle2, fill=self.clr2)

class Motion04(Motion):
    """Круги с дугами"""
    def draw(self, draw_obj):
        # Левый верхний маленький круг
        cr1_x = self.x - (self.w / 4 * self.progress)
        cr1_y = self.y + (self.w / 4 * self.progress)
        cr1_r = self.w * 0.2 * self.progress / 2
        if cr1_r > 0:
            draw_obj.ellipse([
                cr1_x - cr1_r, cr1_y - cr1_r,
                cr1_x + cr1_r, cr1_y + cr1_r
            ], fill=self.clr1)
        
        # Правый нижний маленький круг
        cr2_x = self.x + (self.w / 4 * self.progress)
        cr2_y = self.y - (self.w / 4 * self.progress)
        cr2_r = self.w * 0.2 * self.progress / 2
        if cr2_r > 0:
            draw_obj.ellipse([
                cr2_x - cr2_r, cr2_y - cr2_r,
                cr2_x + cr2_r, cr2_y + cr2_r
            ], fill=self.clr2)
        
        # Правая дуга (верхняя половина круга)
        arc_x = self.x + self.w / 4 * self.progress
        arc_r = self.w / 4
        draw_obj.pieslice([
            arc_x - arc_r, self.y - arc_r,
            arc_x + arc_r, self.y + arc_r
        ], 0, 180, fill=self.clr1)
        
        # Левая дуга (нижняя половина круга)
        arc_x2 = self.x - self.w / 4 * self.progress
        draw_obj.pieslice([
            arc_x2 - arc_r, self.y - arc_r,
            arc_x2 + arc_r, self.y + arc_r
        ], 180, 360, fill=self.clr2)

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
        time.sleep(0.03)  # ~30 FPS
except KeyboardInterrupt:
    print("Exiting...")