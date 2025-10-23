#!/usr/bin/env python
# НАЗВАНИЕ: Шумовой градиент
# ОПИСАНИЕ: Органичные цветные блобы на основе Perlin noise с плавными RGB градиентами
import time
import math
import random
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw
from noise import pnoise3

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
n = 40  # количество блобов (уменьшено для 64x64)
radius = 0
inter = 0.3  # разница между размерами блобов
maxNoise = 15  # шум (адаптировано для меньшего размера)
kMax = random.uniform(0.6, 1.0)
step = 0.01
frame_count = 0

def noise_prog(x):
    return x

def blob_points(size, x_center, y_center, k, t, noisiness):
    """Генерирует точки для одного блоба"""
    points = []
    angle_step = 30  # 360 / 12
    
    for theta in range(0, 390, angle_step):  # 360 + 2 * angle_step
        theta_rad = math.radians(theta)
        
        r1 = math.cos(theta_rad) + 1
        r2 = math.sin(theta_rad) + 1
        
        # Используем Perlin noise
        noise_val = pnoise3(k * r1, k * r2, t, octaves=1, persistence=0.5, lacunarity=2.0)
        r = size + noise_val * noisiness
        
        x = x_center + r * math.cos(theta_rad)
        y = y_center + r * math.sin(theta_rad)
        points.append((x, y))
    
    return points

def generate_frame():
    """Генерирует один кадр анимации"""
    global frame_count
    
    # Создаём изображение
    img = Image.new('RGB', (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    t = frame_count / 100.0
    
    for i in range(n, 0, -1):
        alpha = int(pow(1 - noise_prog(i / n), 3) * 255)
        size = radius + i * inter
        k = kMax * math.sqrt(i / n)
        noisiness = maxNoise * noise_prog(i / n)
        
        # Получаем точки блоба
        points = blob_points(size, 32, 32, k, t - i * step, noisiness)
        
        # Рисуем три блоба с разными цветами (RGB)
        if len(points) > 2:
            # Красный канал
            draw.polygon(points, fill=(255, 0, 0, alpha))
            
            # Зелёный канал (со смещением по времени)
            points_g = blob_points(size, 32, 32, k, t - i * step + 1, noisiness)
            draw.polygon(points_g, fill=(0, 255, 0, alpha))
            
            # Синий канал (со смещением по времени)
            points_b = blob_points(size, 32, 32, k, t - i * step + 2, noisiness)
            draw.polygon(points_b, fill=(0, 0, 255, alpha))
    
    frame_count += 1
    return img

# Анимация
try:
    print("Press CTRL-C to stop.")
    while True:
        frame = generate_frame()
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(0.033)  # ~30 FPS
except KeyboardInterrupt:
    print("Exiting...")
finally:
    matrix.Clear()