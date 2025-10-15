#!/usr/bin/env python
# НАЗВАНИЕ: Волны
# ОПИСАНИЕ: Плавные волнообразные линии на основе Perlin noise
# https://openprocessing.org/sketch/2750462
import time
import math
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw
from opensimplex import OpenSimplex
import numpy as np
import random

import noise  # pip install noise

# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# Параметры анимации
WIDTH = 64
HEIGHT = 64
PALETTE = [
    (255, 0, 216),   # FF00D8
    (255, 178, 1),   # FFB201
    (152, 255, 0),   # 98FF00
    (0, 255, 196),   # 00FFC4
    (0, 130, 254),   # 0082FE
    (183, 51, 255),  # B733FF
]

class Obj:
    def __init__(self, index):
        self.index = index
        self.start_x = random.uniform(0, WIDTH)
        self.frame_count = 0
        self.init()
        
    def init(self):
        range_options = [5, 5, 5, 5, 5, 5, 10, 10, 10, 20, 20, 
                        100, 100, 100, 100, 200, 300]
        self.range_x = random.choice(range_options)
        
        # Масштабирование шага от 5 до 30 в зависимости от range_x
        self.step = self.map_value(self.range_x, 5, 200, 0.5, 3)
        self.str_weight = random.uniform(1, 3)
        self.color = random.choice(PALETTE)
        
        # Альфа канал для маленьких диапазонов
        if self.range_x < 100:
            self.alpha = 150
        else:
            self.alpha = 255
            
        self.is_out = random.random() < 0.1
        
    def map_value(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def move(self):
        self.start_x += self.step
        if self.start_x > WIDTH + self.range_x:
            self.init()
            self.start_x = -self.range_x
            
    def display(self, draw, frame_count):
        points = []
        x = self.start_x
        goal_x = self.start_x + self.range_x
        
        while x <= goal_x and x <= WIDTH:
            if x >= 0:
                # Генерация Perlin noise
                noise_factor = 0.005 if not self.is_out else 0.025
                n = noise.pnoise3(
                    x * 0.001,
                    self.index * noise_factor,
                    frame_count * 0.003
                )
                
                # Масштабирование noise от -HEIGHT*0.25 до HEIGHT*1.25
                y = self.map_value(n, -1, 1, -HEIGHT * 0.25, HEIGHT * 1.25)
                
                if 0 <= y < HEIGHT:
                    points.append((int(x), int(y)))
            x += 1
        
        # Рисование линии
        if len(points) > 1:
            # Применение альфа канала к цвету
            color_with_alpha = tuple(list(self.color) + [self.alpha])
            draw.line(points, fill=self.color, width=int(self.str_weight))

def generate_frame(objs, frame_count):
    # Создаём чёрный фон
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(17, 17, 17))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Обновляем и рисуем все объекты
    for obj in objs:
        obj.move()
        obj.display(draw, frame_count)
    
    return img

# Инициализация объектов
objs_num = 30  # Уменьшено для производительности на LED панели
objs = []
for i in range(objs_num):
    objs.append(Obj(i))

# Анимация
try:
    print("Press CTRL-C to stop.")
    frame_count = 0
    
    while True:
        frame = generate_frame(objs, frame_count)
        matrix.SetImage(frame.convert("RGB"))
        frame_count += 1
        time.sleep(0.016)  # ~60 FPS
        
except KeyboardInterrupt:
    print("\nExiting...")
    matrix.Clear()