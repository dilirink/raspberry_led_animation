#!/usr/bin/env python
# НАЗВАНИЕ: синусойдный текст_:р
# ОПИСАНИЕ: Анимированные текста
import time
import math
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw, ImageFont

# ==================== НАСТРОЙКИ ====================
# Настройки матрицы
MATRIX_ROWS = 64
MATRIX_COLS = 64
MATRIX_CHAIN_LENGTH = 1
MATRIX_PARALLEL = 1
MATRIX_HARDWARE_MAPPING = 'adafruit-hat'

# Настройки анимации
TEXT_STRING = "dilirink_ksenia"
FONT_SIZE = 8  # Размер шрифта в пикселях
CHAR_WIDTH = 6  # Ширина символа (включая интервал)
CHAR_HEIGHT = 8  # Высота символа
FPS = 60  # Кадров в секунду
FRAME_DELAY = 1.0 / FPS  # Задержка между кадрами

# Настройки волнового эффекта
WAVE_SPEED = 0.05  # Скорость волны
WAVE_AMPLITUDE = 1.0  # Амплитуда волны

# Цвет текста (RGB)
TEXT_COLOR = (255, 255, 255)  # Белый
BACKGROUND_COLOR = (0, 0, 0)  # Черный

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = MATRIX_ROWS
options.cols = MATRIX_COLS
options.chain_length = MATRIX_CHAIN_LENGTH
options.parallel = MATRIX_PARALLEL
options.hardware_mapping = MATRIX_HARDWARE_MAPPING

# Создание матрицы
matrix = RGBMatrix(options=options)

# Счетчик кадров
frame_counter = 0

# ==================== ФУНКЦИИ ====================
def generate_frame():
    """Генерация одного кадра с волновым эффектом текста"""
    global frame_counter
    
    # Создаем изображение
    image = Image.new('RGB', (MATRIX_COLS, MATRIX_ROWS), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    
    # Используем встроенный шрифт PIL
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Вычисляем количество ячеек по горизонтали и вертикали
    num_x = MATRIX_COLS // CHAR_WIDTH + 1
    num_y = MATRIX_ROWS // CHAR_HEIGHT + 1
    
    # Для каждой строки вычисляем смещение с помощью синуса
    for j in range(num_y):
        # Вычисляем угол для синусоиды
        angle = frame_counter * WAVE_SPEED + (j / num_y) * (math.pi / 2)
        sine_value = math.sin(angle)
        
        # Маппим значение из диапазона [-1, 1] в [0, num_x*2]
        offset = round((sine_value + WAVE_AMPLITUDE) * num_x)
        
        # Перебираем столбцы и выводим по одному символу в ячейку
        for i in range(num_x):
            # Определяем позицию символа в строке
            pos = (i + j + offset) % len(TEXT_STRING)
            char = TEXT_STRING[pos]
            
            # Координаты для отрисовки
            x = i * CHAR_WIDTH
            y = j * CHAR_HEIGHT
            
            # Рисуем символ
            if font:
                draw.text((x, y), char, fill=TEXT_COLOR, font=font)
            else:
                draw.text((x, y), char, fill=TEXT_COLOR)
    
    frame_counter += 1
    return image

# ==================== ОСНОВНОЙ ЦИКЛ ====================
def main():
    """Основной цикл анимации"""
    try:
        print("LED Matrix Animation Started")
        print(f"Resolution: {MATRIX_COLS}x{MATRIX_ROWS}")
        print(f"Text: '{TEXT_STRING}'")
        print(f"FPS: {FPS}")
        print("Press CTRL-C to stop.")
        print("-" * 40)
        
        while True:
            # Генерируем кадр
            frame = generate_frame()
            
            # Отображаем на матрице
            matrix.SetImage(frame.convert("RGB"))
            
            # Задержка для контроля FPS
            time.sleep(FRAME_DELAY)
            
    except KeyboardInterrupt:
        print("\n" + "-" * 40)
        print("Animation stopped by user")
        print("Exiting...")
    except Exception as e:
        print(f"\nError: {e}")
        print("Exiting...")

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    main()