#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import numpy as np
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

# ==================== НАСТРОЙКИ ====================
# Настройки LED матрицы
MATRIX_ROWS = 64
MATRIX_COLS = 64
MATRIX_CHAIN_LENGTH = 1
MATRIX_PARALLEL = 1
MATRIX_HARDWARE_MAPPING = 'adafruit-hat'

# Параметры анимации
SCALE = 25.0  # масштаб сетки
M = 0.15  # радиус базового круга
FPS = 30  # кадров в секунду
SPEED = 5.0  # скорость анимации

# Цвета (R, G, B)
COLORS = np.array([
    [255, 255, 255],  # белый
    [255, 191, 0],    # желтый
    [0, 127, 191],    # синий
    [255, 63, 0]      # томатно-красный
], dtype=np.uint8)

# ==================== ФУНКЦИИ ====================

def setup_matrix():
    """Настройка LED матрицы"""
    options = RGBMatrixOptions()
    options.rows = MATRIX_ROWS
    options.cols = MATRIX_COLS
    options.chain_length = MATRIX_CHAIN_LENGTH
    options.parallel = MATRIX_PARALLEL
    options.hardware_mapping = MATRIX_HARDWARE_MAPPING
    
    return RGBMatrix(options=options)


def shader_logic_vectorized(t, width, height):
    """
    Векторизованная версия шейдера с использованием numpy
    Возвращает массив RGB значений для всего кадра
    """
    # Создание сеток координат
    x = np.arange(width, dtype=np.float64)
    y = np.arange(height, dtype=np.float64)
    X, Y = np.meshgrid(x, y, indexing='xy')
    
    # Нормализация координат (как в шейдере)
    uv_x = (X - width / 2.0) / height
    uv_y = (Y - height / 2.0) / height
    
    # Сохранение оригинальных UV
    uv0_x, uv0_y = uv_x.copy(), uv_y.copy()
    
    # Округление для сетки
    uv_x = np.round(uv_x * SCALE) / SCALE
    uv_y = np.round(uv_y * SCALE) / SCALE
    
    # Вычисление угла и спирали
    angle = np.arctan2(uv_x, uv_y) + t
    r = M / np.pi * angle
    
    # Применение спирали
    length_uv = np.sqrt(uv_x * uv_x + uv_y * uv_y)
    uv_x = length_uv - r
    
    # Модуло для бесконечного узора
    uv_x = ((uv_x - M) % (2.0 * M)) - M
    
    # Вычисление полосы
    stripe = np.abs(uv_x) / M - M
    stripe -= 0.25
    
    # Возврат к оригинальным UV
    uv_x, uv_y = uv0_x.copy(), uv0_y.copy()
    
    # Модуло для сетки ячеек
    cell_size = 1.0 / SCALE
    uv_x = ((uv_x - cell_size / 2.0) % cell_size) - cell_size / 2.0
    uv_y = ((uv_y - cell_size / 2.0) % cell_size) - cell_size / 2.0
    
    # Вычисление круга в ячейке
    length_cell = np.sqrt(uv_x * uv_x + uv_y * uv_y)
    
    # Вычисление радиуса с защитой от отрицательных значений
    radius_val = M * stripe / SCALE / 2.0
    radius = np.where(radius_val < 0, 0.003, np.maximum(np.sqrt(np.abs(radius_val)), 0.003))
    
    # Круг (1.0 если внутри, 0.0 если снаружи)
    circle = np.where(length_cell <= radius, 1.0, 0.0)
    
    # Возврат к оригинальным UV для цвета
    uv_x, uv_y = uv0_x, uv0_y
    
    # Вычисление строки и столбца
    row = np.round(uv_x * SCALE).astype(np.int32)
    ln = np.round(uv_y * SCALE).astype(np.int32)
    
    # Формула для цвета
    sum_val = ((row % 3) + (ln % 2) + ((row - ln) % 5) * ((row * ln) % 3)) % 4
    sum_val = sum_val.astype(np.int32)
    
    # Получение цветов для всех пикселей
    colors = COLORS[sum_val]  # shape: (height, width, 3)
    
    # Применение круга (затемнение если circle = 0)
    circle_3d = circle[:, :, np.newaxis]  # добавляем ось для RGB
    final_colors = (colors * circle_3d).astype(np.uint8)
    
    return final_colors


def generate_frame(t):
    """Генерация одного кадра анимации"""
    # Получаем массив numpy с RGB значениями
    frame_data = shader_logic_vectorized(t, MATRIX_COLS, MATRIX_ROWS)
    
    # Конвертируем в PIL Image
    # Транспонируем, так как PIL ожидает (height, width, channels)
    img = Image.fromarray(frame_data, mode='RGB')
    
    return img


# ==================== ГЛАВНАЯ ПРОГРАММА ====================

def main():
    """Основной цикл анимации"""
    matrix = setup_matrix()
    
    try:
        print("Анимация запущена. Нажмите CTRL-C для остановки.")
        print(f"Откройте браузер: http://localhost:8888/")
        print(f"Используется numpy для ускорения вычислений")
        start_time = time.time()
        frame_count = 0
        last_fps_time = start_time
        
        while True:
            # Вычисление времени для анимации
            current_time = (time.time() - start_time) * SPEED
            
            # Генерация кадра
            frame = generate_frame(current_time)
            
            # Отображение на матрице
            matrix.SetImage(frame.convert("RGB"))
            
            # Подсчет FPS
            frame_count += 1
            if time.time() - last_fps_time >= 1.0:
                actual_fps = frame_count / (time.time() - last_fps_time)
                print(f"FPS: {actual_fps:.1f}")
                frame_count = 0
                last_fps_time = time.time()
            
            # Задержка для FPS
            time.sleep(1.0 / FPS)
            
    except KeyboardInterrupt:
        print("\nОстановка анимации...")
    finally:
        matrix.Clear()
        print("Завершено.")


if __name__ == "__main__":
    main()