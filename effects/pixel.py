#!/usr/bin/env python
# НАЗВАНИЕ: пиксельная матрица
# ОПИСАНИЕ: сменяймые цвета
import time
import random
import math
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# ==================== НАСТРОЙКИ ====================
# Настройки матрицы
MATRIX_ROWS = 64
MATRIX_COLS = 64
MATRIX_CHAIN_LENGTH = 1
MATRIX_PARALLEL = 1
MATRIX_HARDWARE_MAPPING = 'regular'

# Настройки анимации
PIXEL_GAP = 6  # Расстояние между пикселями
ANIMATION_SPEED = 0.15  # Скорость анимации (0.008-0.25)
FPS = 60  # Кадров в секунду
MAX_TICKER = 360  # Максимальное значение счётчика анимации
COLOR_COUNT = 5  # Количество цветов в палитре

# ===================================================


def rand(min_val, max_val):
    """Генерация случайного числа в диапазоне"""
    return random.uniform(min_val, max_val)


class Pixel:
    def __init__(self, x, y, color, speed, delay, delay_hide, step, bound_size):
        self.x = x
        self.y = y
        self.color = color
        self.speed = rand(0.1, 0.9) * speed
        
        self.size = 0
        self.size_step = rand(0.1, 0.5)  # Увеличил минимальный шаг
        self.min_size = 0.5
        self.max_size_available = bound_size or 2
        self.max_size = rand(self.min_size, self.max_size_available)
        self.size_direction = 1
        
        self.delay = delay
        self.delay_hide = delay_hide
        self.counter = 0
        self.counter_hide = 0
        self.counter_step = step
        
        self.is_hidden = False
        self.is_flicking = False
    
    def draw(self, draw_obj):
        """Рисует пиксель на изображении"""
        # Проверяем, что размер больше минимального порога
        if self.size < 0.5:
            return
        
        center_offset = self.max_size_available * 0.5 - self.size * 0.5
        x1 = int(self.x + center_offset)
        y1 = int(self.y + center_offset)
        x2 = int(self.x + center_offset + self.size)
        y2 = int(self.y + center_offset + self.size)
        
        # Убеждаемся, что x2 > x1 и y2 > y1
        if x2 <= x1:
            x2 = x1 + 1
        if y2 <= y1:
            y2 = y1 + 1
        
        draw_obj.rectangle([x1, y1, x2, y2], fill=self.color)
    
    def show(self):
        """Показывает пиксель с анимацией появления"""
        self.is_hidden = False
        self.counter_hide = 0
        
        if self.counter <= self.delay:
            self.counter += self.counter_step
            return
        
        if self.size >= self.max_size:
            self.is_flicking = True
        
        if self.is_flicking:
            self.flicking()
        else:
            self.size += self.size_step
            if self.size > self.max_size:
                self.size = self.max_size
    
    def hide(self):
        """Скрывает пиксель с анимацией исчезновения"""
        self.counter = 0
        
        if self.counter_hide <= self.delay_hide:
            self.counter_hide += self.counter_step
            if self.is_flicking:
                self.flicking()
            return
        
        self.is_flicking = False
        
        if self.size <= 0:
            self.size = 0
            self.is_hidden = True
            return
        else:
            self.size -= 0.1  # Увеличил скорость исчезновения
            if self.size < 0:
                self.size = 0
    
    def flicking(self):
        """Эффект мерцания пикселя"""
        if self.size >= self.max_size:
            self.size_direction = -1
        elif self.size <= self.min_size:
            self.size_direction = 1
        
        self.size += self.size_direction * self.speed
        
        # Ограничиваем размер
        if self.size > self.max_size:
            self.size = self.max_size
        elif self.size < self.min_size:
            self.size = self.min_size


def get_delay(x, y, width, height, direction=0):
    """Вычисляет задержку на основе расстояния от центра"""
    dx = x - width * 0.5
    dy = y - height if not direction else y
    return math.sqrt(dx ** 2 + dy ** 2)


def init_pixels(width, height):
    """Инициализирует массив пикселей"""
    h = random.randint(0, 360)
    colors = []
    
    for i in range(COLOR_COUNT):
        hue = int(rand(h, h + (i + 1) * 10))
        lightness = int(rand(50, 100))
        # Конвертируем HSL в RGB
        rgb = hsl_to_rgb(hue, 100, lightness)
        colors.append(rgb)
    
    gap = PIXEL_GAP
    step = (width + height) * 0.005
    speed = rand(0.008, 0.25) if ANIMATION_SPEED == 0 else ANIMATION_SPEED
    max_size = int(gap * 0.5)
    
    pixels = []
    
    for x in range(0, width, gap):
        for y in range(0, height, gap):
            if x + max_size > width or y + max_size > height:
                continue
            
            color = random.choice(colors)
            delay = get_delay(x, y, width, height)
            delay_hide = get_delay(x, y, width, height)
            
            pixels.append(Pixel(x, y, color, speed, delay, delay_hide, step, max_size))
    
    return pixels


def hsl_to_rgb(h, s, l):
    """Конвертирует HSL в RGB"""
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0
    
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return (int(r * 255), int(g * 255), int(b * 255))


def main():
    # Конфигурация для матрицы
    options = RGBMatrixOptions()
    options.rows = MATRIX_ROWS
    options.cols = MATRIX_COLS
    options.chain_length = MATRIX_CHAIN_LENGTH
    options.parallel = MATRIX_PARALLEL
    options.hardware_mapping = MATRIX_HARDWARE_MAPPING
    
    matrix = RGBMatrix(options=options)
    
    width = MATRIX_COLS
    height = MATRIX_ROWS
    
    # Инициализация пикселей
    pixels = init_pixels(width, height)
    
    ticker = 0
    animation_direction = 1
    
    print("Press CTRL-C to stop.")
    print(f"Pixels initialized: {len(pixels)}")
    
    try:
        while True:
            # Создаём новый кадр
            frame = Image.new("RGB", (width, height), (0, 0, 0))
            draw = ImageDraw.Draw(frame)
            
            # Управление направлением анимации
            if ticker >= MAX_TICKER:
                animation_direction = -1
            elif ticker <= 0:
                animation_direction = 1
                # Обновляем цвета для новой итерации
                if all(p.is_hidden for p in pixels):
                    print("Reinitializing pixels with new colors...")
                    pixels = init_pixels(width, height)
            
            all_hidden = True
            
            # Обновляем и рисуем каждый пиксель
            for pixel in pixels:
                if animation_direction > 0:
                    pixel.show()
                else:
                    pixel.hide()
                    all_hidden = all_hidden and pixel.is_hidden
                
                pixel.draw(draw)
            
            ticker += animation_direction
            
            if animation_direction < 0 and all_hidden:
                ticker = 0
            
            # Отображаем кадр на матрице
            matrix.SetImage(frame.convert("RGB"))
            time.sleep(1.0 / FPS)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        matrix.Clear()


if __name__ == "__main__":
    main()