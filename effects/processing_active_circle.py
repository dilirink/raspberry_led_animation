#!/usr/bin/env python
# НАЗВАНИЕ: Активные фигуры
# ОПИСАНИЕ: Динамичные геометрические фигуры с плавными анимациями и трансформациями
# https://openprocessing.org/sketch/2421742
import time
import random
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

# Константы
WIDTH = 64
HEIGHT = 64
COLORS = ['#f71735', '#f7d002', '#1A53C0', '#232323']

# Глобальные переменные
objs = []
frame_count = 0

def hex_to_rgb(hex_color):
    """Конвертация HEX в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def ease_in_out_expo(x):
    """Функция плавности анимации"""
    if x == 0:
        return 0
    elif x == 1:
        return 1
    elif x < 0.5:
        return math.pow(2, 20 * x - 10) / 2
    else:
        return (2 - math.pow(2, -20 * x + 10)) / 2

def lerp(start, end, t):
    """Линейная интерполяция"""
    return start + (end - start) * t

def norm(value, start, stop):
    """Нормализация значения"""
    if stop - start == 0:
        return 0
    return (value - start) / (stop - start)

class DynamicShape:
    def __init__(self):
        self.x = random.uniform(0.3, 0.7) * WIDTH
        self.y = random.uniform(0.3, 0.7) * HEIGHT
        self.reduction_ratio = 1
        self.shape_type = random.randint(0, 4)
        self.animation_type = 0
        self.max_action_points = random.randint(2, 4)
        self.action_points = self.max_action_points
        self.elapsed_t = 0
        self.size = 0
        self.size_max = WIDTH * random.uniform(0.01, 0.05)
        self.from_size = 0
        self.is_dead = False
        self.clr = random.choice(COLORS)
        self.change_shape = True
        self.ang = random.randint(0, 1) * math.pi * 0.25
        self.line_sw = 0
        self.from_x = self.x
        self.to_x = self.x
        self.from_y = self.y
        self.to_y = self.y
        self.init()
    
    def init(self):
        """Инициализация параметров анимации"""
        self.elapsed_t = 0
        self.from_size = self.size
        self.to_size = self.size_max * random.uniform(0.5, 1.5)
        self.from_x = self.x
        self.to_x = self.from_x + (WIDTH / 10) * random.choice([-1, 1]) * random.randint(1, 3)
        self.from_y = self.y
        self.to_y = self.from_y + (HEIGHT / 10) * random.choice([-1, 1]) * random.randint(1, 3)
        self.animation_type = random.randint(0, 2)
        self.duration = random.uniform(20, 50)
    
    def draw_shape(self, draw, color_rgb):
        """Отрисовка фигуры"""
        size = self.size * self.reduction_ratio
        cx, cy = int(self.x), int(self.y)
        
        if self.shape_type == 0:  # Заполненный круг
            draw.ellipse([cx - size/2, cy - size/2, cx + size/2, cy + size/2], 
                        fill=color_rgb)
        elif self.shape_type == 1:  # Круг контур
            draw.ellipse([cx - size/2, cy - size/2, cx + size/2, cy + size/2], 
                        outline=color_rgb, width=max(1, int(size * 0.05)))
        elif self.shape_type == 2:  # Заполненный квадрат
            draw.rectangle([cx - size/2, cy - size/2, cx + size/2, cy + size/2], 
                          fill=color_rgb)
        elif self.shape_type == 3:  # Квадрат контур
            s = size * 0.9
            draw.rectangle([cx - s/2, cy - s/2, cx + s/2, cy + s/2], 
                          outline=color_rgb, width=max(1, int(size * 0.05)))
        elif self.shape_type == 4:  # Крест
            line_width = max(1, int(size * 0.05))
            draw.line([cx, cy - size*0.45, cx, cy + size*0.45], 
                     fill=color_rgb, width=line_width)
            draw.line([cx - size*0.45, cy, cx + size*0.45, cy], 
                     fill=color_rgb, width=line_width)
        
        # Линия следа
        if self.line_sw > 0:
            draw.line([int(self.x), int(self.y), int(self.from_x), int(self.from_y)], 
                     fill=color_rgb, width=max(1, int(self.line_sw)))
    
    def move(self):
        """Обновление анимации"""
        if self.duration > 0:
            n = ease_in_out_expo(norm(self.elapsed_t, 0, self.duration))
        else:
            n = 1
        
        if 0 < self.elapsed_t < self.duration:
            if self.action_points == self.max_action_points:
                self.size = lerp(0, self.size_max, n)
            elif self.action_points > 0:
                if self.animation_type == 0:
                    self.size = lerp(self.from_size, self.to_size, n)
                elif self.animation_type == 1:
                    self.x = lerp(self.from_x, self.to_x, n)
                    self.line_sw = lerp(0, self.size / 5, math.sin(n * math.pi))
                elif self.animation_type == 2:
                    self.y = lerp(self.from_y, self.to_y, n)
                    self.line_sw = lerp(0, self.size / 5, math.sin(n * math.pi))
                elif self.animation_type == 3:
                    if self.change_shape:
                        self.shape_type = random.randint(0, 4)
                        self.change_shape = False
                self.reduction_ratio = lerp(1, 0.3, math.sin(n * math.pi))
            else:
                self.size = lerp(self.from_size, 0, n)
        
        self.elapsed_t += 1
        
        if self.elapsed_t > self.duration:
            self.action_points -= 1
            self.init()
        
        if self.action_points < 0:
            self.is_dead = True

def generate_frame():
    """Генерация одного кадра анимации"""
    global objs, frame_count
    
    # Создание изображения
    image = Image.new('RGB', (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Отрисовка всех объектов
    for obj in objs:
        color_rgb = hex_to_rgb(obj.clr)
        obj.draw_shape(draw, color_rgb)
        obj.move()
    
    # Добавление новых объектов
    if frame_count % random.choice([15, 30]) == 0:
        add_num = random.randint(1, 30)
        for _ in range(add_num):
            objs.append(DynamicShape())
    
    # Удаление мертвых объектов
    objs[:] = [obj for obj in objs if not obj.is_dead]
    
    frame_count += 1
    
    return image

# Основной цикл анимации
try:
    print("Starting animation... Press CTRL-C to stop.")
    
    # Добавляем первый объект
    objs.append(DynamicShape())
    
    while True:
        frame = generate_frame()
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(0.033)  # ~30 FPS
        
except KeyboardInterrupt:
    print("\nExiting...")
    matrix.Clear()