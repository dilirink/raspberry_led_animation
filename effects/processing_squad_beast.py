#!/usr/bin/env python
# НАЗВАНИЕ: Квадратный зверь
# ОПИСАНИЕ: Динамические анимированные прямоугольники с плавными трансформациями
# https://openprocessing.org/sketch/2343601
import time
import random
import math
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

# Функция плавности (easing)
def ease_in_out_quint(x):
    return 16 * x * x * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 5) / 2

# Функция интерполяции
def lerp(start, end, t):
    return start + (end - start) * t

# Класс прямоугольника
class SuperRect:
    def __init__(self, x, y, w, h, a, sep, clr):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.a = a
        self.clr = clr
        self.separate = sep
        self.origin_w = w
        self.origin_h = h
        self.toggle = False
        self.duration = 90
        self.time = 0
        self.from_w = w
        self.from_h = h
        self.to_w = w
        self.to_h = h
        self.set_values()
        self.w = self.to_w
        self.h = self.to_h
        self.set_values()
        
    def set_values(self):
        self.from_w = self.w
        self.to_w = (self.origin_w / self.separate) * random.randint(1, self.separate)
        self.from_h = self.h
        self.to_h = (self.origin_h / self.separate) * random.randint(1, self.separate)
        self.time = 0
        
    def move(self, frame_count):
        if self.toggle:
            self.time += 1
            if 0 < self.time < self.duration:
                n = self.time / self.duration
                self.w = lerp(self.from_w, self.to_w, ease_in_out_quint(n))
                self.h = lerp(self.from_h, self.to_h, ease_in_out_quint(n))
            elif self.time > self.duration:
                self.toggle = False
                
        if not self.toggle and frame_count % 30 == 0 and random.random() < 0.1:
            self.toggle = True
            self.time = 0
            self.set_values()

# Инициализация
colors = [(247, 23, 53), (9, 62, 128), (236, 195, 11), (255, 255, 255), (42, 189, 228)]
rows = 3
cols = 3
width = 64
height = 64
grid_w = width * 0.9
grid_h = height * 0.9
cell_w = grid_w / cols
cell_h = grid_h / rows
sep = 4

rects = []

# Создание прямоугольников
for i in range(cols):
    for j in range(rows):
        x = i * cell_w + cell_w / 2
        y = j * cell_h + cell_h / 2
        rect_size = cell_w * 0.6
        random.shuffle(colors)
        
        rects.append(SuperRect(x - (rect_size / 2), y - (rect_size / 2), 
                              rect_size, rect_size, 0, sep, colors[1]))
        rects.append(SuperRect(x + (rect_size / 2), y - (rect_size / 2), 
                              rect_size, rect_size, math.pi * 0.5, sep, colors[2]))
        rects.append(SuperRect(x + (rect_size / 2), y + (rect_size / 2), 
                              rect_size, rect_size, math.pi, sep, colors[3]))
        rects.append(SuperRect(x - (rect_size / 2), y + (rect_size / 2), 
                              rect_size, rect_size, math.pi * 1.5, sep, colors[4]))

random.shuffle(rects)

# Функция для генерации кадра
def generate_frame(frame_count):
    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    offset_x = (width - grid_w) / 2
    offset_y = (height - grid_h) / 2
    
    # Отрисовка заполненных прямоугольников
    for r in rects:
        cos_a = math.cos(r.a)
        sin_a = math.sin(r.a)
        
        # Углы прямоугольника
        corners = [
            (0, 0),
            (r.w, 0),
            (r.w, r.h),
            (0, r.h)
        ]
        
        # Поворот и смещение
        rotated = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + r.x + offset_x
            ry = cx * sin_a + cy * cos_a + r.y + offset_y
            rotated.append((rx, ry))
        
        draw.polygon(rotated, fill=r.clr)
    
    # Отрисовка границ
    for r in rects:
        cos_a = math.cos(r.a)
        sin_a = math.sin(r.a)
        
        corners = [
            (0, 0),
            (r.w, 0),
            (r.w, r.h),
            (0, r.h)
        ]
        
        rotated = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + r.x + offset_x
            ry = cx * sin_a + cy * cos_a + r.y + offset_y
            rotated.append((rx, ry))
        
        draw.polygon(rotated, outline=(0, 0, 0), width=1)
    
    # Обновление прямоугольников
    for r in rects:
        r.move(frame_count)
    
    return image

# Анимация
try:
    print("Press CTRL-C to stop.")
    frame_count = 0
    while True:
        frame = generate_frame(frame_count)
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(0.033)  # ~30 FPS
        frame_count += 1
except KeyboardInterrupt:
    print("Exiting...")