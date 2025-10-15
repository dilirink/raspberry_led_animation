#!/usr/bin/env python
# НАЗВАНИЕ: Гравитация кругов
# ОПИСАНИЕ: Движущиеся цветные круги с взаимодействием и соединительными линиями
# https://openprocessing.org/sketch/2642304
import time
import random
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw

import math
# ==================== БЛОК НАСТРОЕК ====================
# Настройки матрицы
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64

# Настройки анимации
CIRCLE_COUNT = 20           # Количество кругов (рекомендуется 15-30)
CIRCLE_SIZE_MIN = 0.02      # Минимальный размер круга (относительно ширины матрицы)
CIRCLE_SIZE_MAX = 0.1      # Максимальный размер круга (относительно ширины матрицы)
CIRCLE_SPEED_MIN = -0.3     # Минимальная скорость движения
CIRCLE_SPEED_MAX = 0.3      # Максимальная скорость движения

# Настройки мостов между кругами
DRAW_BRIDGES = True         # Рисовать ли мосты между кругами
BRIDGE_THICKNESS = 2        # Толщина линии моста в пикселях (1-5)
BRIDGE_MAX_DISTANCE = 30    # Максимальное расстояние для создания моста (в пикселях)
BRIDGE_MIN_DISTANCE = 0     # Минимальное расстояние для создания моста (в пикселях)
BRIDGE_ZONE_RADIUS = 0.15   # Радиус зоны вокруг круга для создания мостов (относительно размера матрицы)

# Настройки физики
COLLISION_FORCE = 0.01      # Сила отталкивания при столкновении (0.001-0.05)

# Скорость анимации
FPS = 30                    # Кадров в секунду (10-30)

# Цветовая палитра
COLORS = ['#08804e', '#f0bd15', '#d10406', '#fd7800', '#2abde4', '#f3f7fa', '#574689']
BACKGROUND_COLOR = '#212121'

# ==================== КОНЕЦ БЛОКА НАСТРОЕК ====================

# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = MATRIX_HEIGHT
options.cols = MATRIX_WIDTH
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# Класс для движущихся кругов
class Mover:
    def __init__(self, x, y, d, clr):
        self.x = x
        self.y = y
        self.d = d
        self.clr = clr
        self.vx = random.uniform(CIRCLE_SPEED_MIN, CIRCLE_SPEED_MAX)
        self.vy = random.uniform(CIRCLE_SPEED_MIN, CIRCLE_SPEED_MAX)
    
    def move(self, width, height):
        self.x += self.vx
        self.y += self.vy
        radius = self.d / 2
        
        if self.x < radius or self.x > width - radius:
            self.vx *= -1
        if self.y < radius or self.y > height - radius:
            self.vy *= -1
        
        self.x = max(radius, min(width - radius, self.x))
        self.y = max(radius, min(height - radius, self.y))

# Инициализация кругов
circles = []

print(f"Инициализация {CIRCLE_COUNT} кругов...")
for i in range(CIRCLE_COUNT):
    x = MATRIX_WIDTH * random.uniform(0.1, 0.9)
    y = MATRIX_HEIGHT * random.uniform(0.1, 0.9)
    d = MATRIX_WIDTH * random.uniform(CIRCLE_SIZE_MIN, CIRCLE_SIZE_MAX)
    clr = COLORS[i % len(COLORS)]
    circles.append(Mover(x, y, d, clr))

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_bridge(draw, x1, y1, d1, x2, y2, d2, clr1, clr2):
    """Рисует мост между двумя кругами с учётом всех настроек"""
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Проверка: находится ли второй круг в зоне для создания моста
    if distance < BRIDGE_MIN_DISTANCE or distance > BRIDGE_MAX_DISTANCE:
        return
    
    # Дополнительная проверка с учётом радиуса зоны
    r = min(MATRIX_WIDTH, MATRIX_HEIGHT) * BRIDGE_ZONE_RADIUS
    r1 = d1 / 2
    r2 = d2 / 2
    R1 = r1 + r
    R2 = r2 + r
    
    if distance > R1 + R2 or distance == 0:
        return
    
    dirX = dx / distance
    dirY = dy / distance
    
    a = (R1 * R1 - R2 * R2 + distance * distance) / (2 * distance)
    underRoot = R1 * R1 - a * a
    
    if underRoot < 0:
        return
    
    h = math.sqrt(underRoot)
    
    midX = x1 + dirX * a
    midY = y1 + dirY * a
    
    perpX = -dirY * h
    perpY = dirX * h
    
    cx1 = midX + perpX
    cy1 = midY + perpY
    cx2 = midX - perpX
    cy2 = midY - perpY
    
    if math.sqrt((cx1-cx2)**2 + (cy1-cy2)**2) < r * 2:
        return
    
    # Рисование моста с заданной толщиной
    rgb1 = hex_to_rgb(clr1)
    rgb2 = hex_to_rgb(clr2)
    avg_color = tuple((c1 + c2) // 2 for c1, c2 in zip(rgb1, rgb2))
    
    draw.line([(x1, y1), (x2, y2)], fill=avg_color, width=BRIDGE_THICKNESS)

def generate_frame():
    img = Image.new('RGB', (MATRIX_WIDTH, MATRIX_HEIGHT), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Рисуем мосты между кругами
    if DRAW_BRIDGES:
        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                c1 = circles[i]
                c2 = circles[j]
                draw_bridge(draw, c1.x, c1.y, c1.d, c2.x, c2.y, c2.d, c1.clr, c2.clr)
    
    # Рисуем круги
    for c in circles:
        rgb = hex_to_rgb(c.clr)
        x0 = c.x - c.d/2
        y0 = c.y - c.d/2
        x1 = c.x + c.d/2
        y1 = c.y + c.d/2
        draw.ellipse([x0, y0, x1, y1], fill=rgb)
    
    # Двигаем круги
    for c in circles:
        c.move(MATRIX_WIDTH, MATRIX_HEIGHT)
    
    # Обработка коллизий
    for i in range(len(circles)):
        c1 = circles[i]
        for j in range(i + 1, len(circles)):
            c2 = circles[j]
            dx = c2.x - c1.x
            dy = c2.y - c1.y
            distance = math.sqrt(dx * dx + dy * dy)
            min_dist = c1.d + c2.d
            
            if distance < min_dist and distance > 0:
                force = (min_dist - distance) * COLLISION_FORCE
                nx = dx / distance
                ny = dy / distance
                c1.vx -= force * nx
                c1.vy -= force * ny
                c2.vx += force * nx
                c2.vy += force * ny
    
    return img

# Анимация
try:
    print(f"Запуск анимации ({FPS} FPS)...")
    print(f"Настройки мостов:")
    print(f"  - Толщина: {BRIDGE_THICKNESS} пикселей")
    print(f"  - Макс. расстояние: {BRIDGE_MAX_DISTANCE} пикселей")
    print(f"  - Мин. расстояние: {BRIDGE_MIN_DISTANCE} пикселей")
    print(f"  - Радиус зоны: {BRIDGE_ZONE_RADIUS} (относительно размера матрицы)")
    print("Press CTRL-C to stop.")
    frame_delay = 1.0 / FPS
    
    while True:
        frame = generate_frame()
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(frame_delay)
except KeyboardInterrupt:
    print("\nExiting...")
    matrix.Clear()