#!/usr/bin/env python
"""
LED Matrix Shader Animation
Based on shader by Matthias Hurrle (@atzedent)
Ported to Python for 64x64 LED matrix
OPTIMIZED VERSION with numpy vectorization
"""

import time
import numpy as np
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

# ============= НАСТРОЙКИ =============
# Параметры матрицы
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
CHAIN_LENGTH = 1
PARALLEL = 1
HARDWARE_MAPPING = 'adafruit-hat'

# Параметры анимации
FPS = 60  # Кадров в секунду
FRAME_DELAY = 1.0 / FPS
SCALE = 2.4  # Масштаб паттерна
NUM_PARTICLES = 20  # Количество светящихся точек
INTENSITY = 0.00125  # Интенсивность свечения

# ======================================


class ShaderRenderer:
    """Оптимизированный рендерер с предвычислениями"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.min_dim = min(width, height)
        
        # Предвычисление сетки координат
        x = np.arange(width, dtype=np.float32)
        y = np.arange(height, dtype=np.float32)
        xx, yy = np.meshgrid(x, y)
        
        # UV координаты [-1, 1]
        self.uv_x = (xx - width * 0.5) / self.min_dim
        self.uv_y = (yy - height * 0.5) / self.min_dim
        
        # Предвычисление полярных координат
        self.angle = np.arctan2(self.uv_y, self.uv_x)
        self.radius = np.sqrt(self.uv_x**2 + self.uv_y**2)
        
        # Предвычисление параметров частиц
        self.particle_params = []
        for i in range(1, NUM_PARTICLES + 1):
            a = self.rnd(float(i))
            nx = a
            ny = np.fmod(a * 34.56, 1.0)
            self.particle_params.append((nx, ny, i))
    
    @staticmethod
    def rnd(a):
        """Псевдослучайное число"""
        px = np.fmod(a * 12.9898, 1.0)
        py = np.fmod(a * 78.233, 1.0)
        px += px * py * 345.0
        py += px * py * 345.0
        return np.fmod(px * py, 1.0)
    
    @staticmethod
    def hue(a):
        """Преобразование в RGB через HSV (векторизовано)"""
        # a может быть массивом
        r = 0.6 + 0.6 * np.cos(6.3 * a)
        g = 0.6 + 0.6 * np.cos(6.3 * a + 83)
        b = 0.6 + 0.6 * np.cos(6.3 * a + 21)
        return np.stack([r, g, b], axis=-1)
    
    def generate_frame(self, time_val):
        """Генерация кадра с векторизацией numpy"""
        # Трансформация координат (туннельный эффект)
        safe_radius = np.maximum(self.radius, 0.001)
        uv_u = self.angle * 5.0 / 6.28318
        uv_v = 0.05 / np.tan(safe_radius + 0.001) + time_val
        
        # Фрактальная часть
        uv_u = np.fmod(uv_u + 0.5, 1.0) - 0.5
        uv_v = np.fmod(uv_v + 0.5, 1.0) - 0.5
        
        # Масштабирование
        uv_u *= SCALE
        uv_v *= SCALE
        
        # Инициализация цветового массива
        col = np.zeros((self.height, self.width, 3), dtype=np.float32)
        
        # Вычисление вклада каждой частицы (векторизовано)
        for nx, ny, i in self.particle_params:
            # Позиция частицы
            px = np.sin(nx * (time_val + 7.0) + time_val * 0.5)
            py = np.sin(ny * (time_val + 7.0) + time_val * 0.5)
            
            # Расстояние до частицы
            dx = uv_u - px
            dy = uv_v - py
            d = dx**2 + dy**2
            
            # Защита от деления на ноль
            d = np.maximum(d, 1e-6)
            
            # Интенсивность
            intensity = INTENSITY / d
            
            # Цвет с учетом позиции
            uv_dot = self.uv_x**2 + self.uv_y**2
            hue_val = uv_dot + i * 0.125 + time_val
            color = self.hue(hue_val)
            
            # Добавление вклада
            col += (intensity[..., np.newaxis] * color)
        
        # Преобразование в RGB [0-255]
        col = np.clip(col * 255, 0, 255).astype(np.uint8)
        
        return Image.fromarray(col, 'RGB')


def generate_frame(time_val):
    """Обертка для совместимости"""
    return renderer.generate_frame(time_val)


def main():
    """Основная функция запуска анимации"""
    global renderer
    
    # Конфигурация матрицы
    options = RGBMatrixOptions()
    options.rows = MATRIX_HEIGHT
    options.cols = MATRIX_WIDTH
    options.chain_length = CHAIN_LENGTH
    options.parallel = PARALLEL
    options.hardware_mapping = HARDWARE_MAPPING
    
    # Инициализация матрицы
    matrix = RGBMatrix(options=options)
    
    # Инициализация оптимизированного рендерера
    renderer = ShaderRenderer(MATRIX_WIDTH, MATRIX_HEIGHT)
    
    # print("=" * 50)
    # print("LED Matrix Shader Animation [OPTIMIZED]")
    # print("=" * 50)
    # print(f"Resolution: {MATRIX_WIDTH}x{MATRIX_HEIGHT}")
    # print(f"Target FPS: {FPS}")
    # print(f"Particles: {NUM_PARTICLES}")
    # print("Press CTRL-C to stop.")
    # print("-" * 50)
    
    start_time = time.time()
    frame_count = 0
    fps_update_interval = 30  # Обновлять статистику каждые 30 кадров
    
    try:
        while True:
            frame_start = time.time()
            
            # Текущее время для анимации
            current_time = time.time() - start_time
            
            # Генерация кадра
            frame = renderer.generate_frame(current_time)
            
            # Отображение на матрице
            matrix.SetImage(frame.convert("RGB"))
            
            frame_count += 1
            
            # Статистика производительности
            if frame_count % fps_update_interval == 0:
                elapsed = time.time() - start_time
                fps_actual = frame_count / elapsed
                frame_time = (time.time() - frame_start) * 1000
                # print(f"Frames: {frame_count:5d} | "
                #       f"FPS: {fps_actual:5.1f} | "
                #       f"Frame time: {frame_time:5.1f}ms")
            
            # Задержка для поддержания целевого FPS
            frame_elapsed = time.time() - frame_start
            sleep_time = max(0, FRAME_DELAY - frame_elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        # print("\n" + "=" * 50)
        # print("Stopping animation...")
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        # print(f"Total frames: {frame_count}")
        # print(f"Average FPS: {avg_fps:.1f}")
        # print(f"Runtime: {elapsed:.1f}s")
        # print("=" * 50)
        # print("Goodbye! 👋")


if __name__ == "__main__":
    main()