#!/usr/bin/env python
import time
import random
import math
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# ===== НАСТРОЙКИ =====
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
FIRE_WIDTH = 64
FIRE_HEIGHT = 64
FPS = 14
DECAY = 2  # Скорость затухания пламени (1-10)
INTENSITY = 8  # Интенсивность огня (1-15)
COOLING = 30  # Охлаждение пламени (10-50)
PALETTE_STYLE = "blue"  # "classic", "blue", "purple"

# Настройки матрицы
options = RGBMatrixOptions()
options.rows = MATRIX_HEIGHT
options.cols = MATRIX_WIDTH
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# ===== ЦВЕТОВАЯ ПАЛИТРА =====
def create_fire_palette(style="classic"):
    palette = []
    
    if style == "classic":
        # Классическое огненное пламя
        for i in range(256):
            if i < 32:
                # Черный -> Темно-красный
                palette.append((i*2, 0, 0))
            elif i < 64:
                # Темно-красный -> Красный
                palette.append((64 + (i-32)*4, (i-32)*4, 0))
            elif i < 96:
                # Красный -> Оранжевый
                palette.append((255, 64 + (i-64)*4, 0))
            elif i < 128:
                # Оранжевый -> Желтый
                palette.append((255, 128 + (i-96)*4, (i-96)*2))
            else:
                # Желтый -> Белый
                val = 128 + (i-128)*2
                palette.append((255, min(255, val), min(255, val)))
                
    elif style == "blue":
        # Синее пламя
        for i in range(256):
            if i < 64:
                palette.append((0, 0, i*2))
            elif i < 128:
                palette.append((0, (i-64)*2, 128 + (i-64)*2))
            else:
                val = (i-128)*4
                palette.append((min(255, val), min(255, val), 255))
                
    elif style == "purple":
        # Фиолетовое пламя
        for i in range(256):
            if i < 64:
                palette.append((i, 0, i*2))
            elif i < 128:
                palette.append((64 + (i-64)*2, 0, 128 + (i-64)*2))
            else:
                val = (i-128)*4
                palette.append((128 + val, min(255, val//2), 192 + val//2))
    
    return palette

# Создаем палитру
fire_palette = create_fire_palette(PALETTE_STYLE)

# ===== АЛГОРИТМ ПЛАМЕНИ =====
class FireEffect:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fire_array = [[0 for _ in range(width)] for _ in range(height)]
        self.spark_chance = 0.3  # Вероятность появления искры
        
    def update_fire(self):
        # Обновляем основание пламени
        for x in range(self.width):
            # Добавляем случайные искры в основание
            if random.random() < self.spark_chance:
                self.fire_array[self.height-1][x] = min(255, self.fire_array[self.height-1][x] + random.randint(150, 255))
            else:
                # Плавное затухание у основания
                self.fire_array[self.height-1][x] = max(0, self.fire_array[self.height-1][x] - DECAY)
            
            # Обеспечиваем минимальную активность у основания
            if self.fire_array[self.height-1][x] < 30:
                self.fire_array[self.height-1][x] = random.randint(20, 60)
        
        # Распространяем пламя вверх
        for y in range(self.height-2, -1, -1):
            for x in range(self.width):
                # Собираем значения от соседних пикселей снизу
                bottom_val = self.fire_array[y+1][x]
                left_val = self.fire_array[y+1][x-1] if x > 0 else bottom_val
                right_val = self.fire_array[y+1][(x+1) % self.width] if x < self.width-1 else bottom_val
                
                # Усредняем и добавляем случайность
                avg = (bottom_val + left_val + right_val) // 3
                random_offset = random.randint(-COOLING, INTENSITY)
                
                new_val = max(0, min(255, avg + random_offset))
                self.fire_array[y][x] = new_val
    
    def create_fire_image(self):
        image = Image.new("RGB", (self.width, self.height))
        pixels = image.load()
        
        for y in range(self.height):
            for x in range(self.width):
                fire_val = self.fire_array[y][x]
                color_index = min(255, max(0, fire_val))
                pixels[x, y] = fire_palette[color_index]
        
        return image

# ===== ОСНОВНОЙ ЦИКЛ =====
def main():
    fire = FireEffect(FIRE_WIDTH, FIRE_HEIGHT)
    
    try:
        print("Fire effect started. Press CTRL-C to stop.")
        print(f"Settings: FPS={FPS}, DECAY={DECAY}, INTENSITY={INTENSITY}")
        print(f"Palette: {PALETTE_STYLE}")
        
        while True:
            start_time = time.time()
            
            # Обновляем и отрисовываем пламя
            fire.update_fire()
            fire_image = fire.create_fire_image()
            
            # Выводим на матрицу
            matrix.SetImage(fire_image.convert("RGB"))
            
            # Поддерживаем стабильный FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, 1.5/FPS - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nExiting fire effect...")
        # Гасим матрицу
        matrix.Clear()

if __name__ == "__main__":
    main()