#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Красивая анимация алгоритма сортировки для LED панели 64x64
"""

import time
import random
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

# ========== НАСТРОЙКИ ==========
# Параметры LED матрицы
MATRIX_ROWS = 64
MATRIX_COLS = 64
CHAIN_LENGTH = 1
PARALLEL = 1
HARDWARE_MAPPING  = 'adafruit-hat'

# Параметры анимации
ANIMATION_SPEED = 0.05  # Задержка между кадрами (секунды)
ARRAY_SIZE = 64  # Количество элементов для сортировки
BAR_WIDTH = 1  # Ширина столбца

# Цветовая схема (RGB)
COLOR_DEFAULT = (0, 150, 255)  # Синий - обычные элементы
COLOR_COMPARING = (255, 255, 0)  # Желтый - сравниваемые элементы
COLOR_SWAPPING = (255, 0, 0)  # Красный - элементы при обмене
COLOR_SORTED = (0, 255, 0)  # Зеленый - отсортированные элементы
COLOR_PIVOT = (255, 0, 255)  # Пурпурный - опорный элемент
COLOR_BACKGROUND = (0, 0, 0)  # Черный - фон
# ==============================


class SortVisualizer:
    """Класс для визуализации алгоритмов сортировки"""
    
    def __init__(self, matrix, array_size):
        self.matrix = matrix
        self.width = MATRIX_COLS
        self.height = MATRIX_ROWS
        self.array_size = min(array_size, self.width)
        self.array = list(range(1, self.height + 1))
        random.shuffle(self.array)
        self.sorted_indices = set()
        
    def draw_array(self, comparing=[], swapping=[], pivot=-1):
        """Отрисовка массива в виде столбцов"""
        image = Image.new("RGB", (self.width, self.height), COLOR_BACKGROUND)
        draw = ImageDraw.Draw(image)
        
        bar_width = max(1, self.width // self.array_size)
        
        for i in range(self.array_size):
            x = i * bar_width
            height = self.array[i]
            y = self.height - height
            
            # Выбор цвета в зависимости от состояния
            if i == pivot:
                color = COLOR_PIVOT
            elif i in swapping:
                color = COLOR_SWAPPING
            elif i in comparing:
                color = COLOR_COMPARING
            elif i in self.sorted_indices:
                color = COLOR_SORTED
            else:
                color = COLOR_DEFAULT
            
            # Рисуем столбец
            for bw in range(bar_width):
                if x + bw < self.width:
                    draw.rectangle([x + bw, y, x + bw, self.height - 1], fill=color)
        
        return image
    
    def update_display(self, comparing=[], swapping=[], pivot=-1):
        """Обновление дисплея"""
        frame = self.draw_array(comparing, swapping, pivot)
        self.matrix.SetImage(frame.convert("RGB"))
        time.sleep(ANIMATION_SPEED)
    
    def show_algorithm_name(self, algorithm):
        """Отображение названия алгоритма на 3 секунды"""
        # Словарь с названиями алгоритмов
        algorithm_names = {
            'bubble': 'BUBBLE\nSORT',
            'quick': 'QUICK\nSORT',
            'insertion': 'INSERT\nSORT',
            'selection': 'SELECT\nSORT'
        }
        
        text = algorithm_names.get(algorithm, algorithm.upper())
        
        # Создаем изображение с текстом
        image = Image.new("RGB", (self.width, self.height), COLOR_BACKGROUND)
        draw = ImageDraw.Draw(image)
        
        # Пытаемся загрузить шрифт, если не получается - используем дефолтный
        try:
            # Пробуем разные размеры шрифта
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            except:
                font = ImageFont.load_default()
        
        # Разбиваем текст на строки
        lines = text.split('\n')
        
        # Вычисляем общую высоту текста
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
        
        total_height = sum(line_heights) + (len(lines) - 1) * 2  # 2px между строками
        y_offset = (self.height - total_height) // 2
        
        # Рисуем каждую строку по центру
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.width - text_width) // 2
            y = y_offset
            
            # Рисуем текст с эффектом свечения (рисуем несколько раз со смещением)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 50, 100))
            
            # Основной текст
            draw.text((x, y), line, font=font, fill=(0, 200, 255))
            
            y_offset += text_height + 2
        
        # Отображаем на матрице 3 секунды
        self.matrix.SetImage(image.convert("RGB"))
        time.sleep(3)
    
    # ===== АЛГОРИТМЫ СОРТИРОВКИ =====
    
    def bubble_sort(self):
        """Сортировка пузырьком"""
        n = self.array_size
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                self.update_display(comparing=[j, j + 1])
                
                if self.array[j] > self.array[j + 1]:
                    self.update_display(swapping=[j, j + 1])
                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    swapped = True
                    self.update_display(swapping=[j, j + 1])
            
            self.sorted_indices.add(n - i - 1)
            
            if not swapped:
                break
        
        # Отметить все как отсортированные
        for i in range(n):
            self.sorted_indices.add(i)
        self.update_display()
    
    def quick_sort(self, low=0, high=None):
        """Быстрая сортировка"""
        if high is None:
            high = self.array_size - 1
        
        if low < high:
            pi = self.partition(low, high)
            self.quick_sort(low, pi - 1)
            self.quick_sort(pi + 1, high)
        
        # Если вся область отсортирована
        if low == 0 and high == self.array_size - 1:
            for i in range(self.array_size):
                self.sorted_indices.add(i)
            self.update_display()
    
    def partition(self, low, high):
        """Разделение для быстрой сортировки"""
        pivot = self.array[high]
        i = low - 1
        
        for j in range(low, high):
            self.update_display(comparing=[j, high], pivot=high)
            
            if self.array[j] < pivot:
                i += 1
                self.update_display(swapping=[i, j], pivot=high)
                self.array[i], self.array[j] = self.array[j], self.array[i]
                self.update_display(swapping=[i, j], pivot=high)
        
        self.update_display(swapping=[i + 1, high], pivot=high)
        self.array[i + 1], self.array[high] = self.array[high], self.array[i + 1]
        self.update_display(swapping=[i + 1, high])
        
        self.sorted_indices.add(i + 1)
        return i + 1
    
    def insertion_sort(self):
        """Сортировка вставками"""
        for i in range(1, self.array_size):
            key = self.array[i]
            j = i - 1
            
            self.update_display(comparing=[i])
            
            while j >= 0 and self.array[j] > key:
                self.update_display(comparing=[j, j + 1])
                self.array[j + 1] = self.array[j]
                self.update_display(swapping=[j, j + 1])
                j -= 1
            
            self.array[j + 1] = key
            self.sorted_indices.add(i)
            self.update_display()
        
        for i in range(self.array_size):
            self.sorted_indices.add(i)
        self.update_display()
    
    def selection_sort(self):
        """Сортировка выбором"""
        for i in range(self.array_size):
            min_idx = i
            
            for j in range(i + 1, self.array_size):
                self.update_display(comparing=[min_idx, j])
                
                if self.array[j] < self.array[min_idx]:
                    min_idx = j
            
            if min_idx != i:
                self.update_display(swapping=[i, min_idx])
                self.array[i], self.array[min_idx] = self.array[min_idx], self.array[i]
                self.update_display(swapping=[i, min_idx])
            
            self.sorted_indices.add(i)
            self.update_display()
        
        for i in range(self.array_size):
            self.sorted_indices.add(i)
        self.update_display()
    
    def run_sort(self, algorithm='bubble'):
        """Запуск выбранного алгоритма"""
        print(f"Запуск алгоритма: {algorithm}")
        
        # Показываем название алгоритма на 3 секунды
        self.show_algorithm_name(algorithm)
        
        if algorithm == 'bubble':
            self.bubble_sort()
        elif algorithm == 'quick':
            self.quick_sort()
        elif algorithm == 'insertion':
            self.insertion_sort()
        elif algorithm == 'selection':
            self.selection_sort()
        else:
            print(f"Неизвестный алгоритм: {algorithm}")
            self.bubble_sort()
        
        # Показываем финальный результат 2 секунды
        time.sleep(2)


def main():
    """Главная функция"""
    # Инициализация матрицы
    options = RGBMatrixOptions()
    options.rows = MATRIX_ROWS
    options.cols = MATRIX_COLS
    options.chain_length = CHAIN_LENGTH
    options.parallel = PARALLEL
    options.hardware_mapping = HARDWARE_MAPPING
    
    matrix = RGBMatrix(options=options)
    
    # Список всех доступных алгоритмов
    algorithms = ['bubble', 'quick', 'insertion', 'selection']
    
    # Рандомизируем порядок один раз при старте
    random.shuffle(algorithms)
    
    try:
        print("=" * 50)
        print("Анимация сортировки для LED панели 64x64")
        print("=" * 50)
        print(f"Порядок алгоритмов: {' -> '.join(algorithms)}")
        print(f"Размер массива: {ARRAY_SIZE}")
        print(f"Скорость анимации: {ANIMATION_SPEED}s")
        print("Нажмите CTRL-C для остановки")
        print("=" * 50)
        
        algorithm_index = 0
        
        while True:
            # Выбираем текущий алгоритм из списка
            current_algorithm = algorithms[algorithm_index]
            
            visualizer = SortVisualizer(matrix, ARRAY_SIZE)
            visualizer.update_display()
            time.sleep(1)
            
            visualizer.run_sort(current_algorithm)
            
            # Переходим к следующему алгоритму (циклически)
            algorithm_index = (algorithm_index + 1) % len(algorithms)
            
            # Пауза перед следующей итерацией
            time.sleep(2)
            print(f"Следующий алгоритм: {algorithms[algorithm_index]}")
            
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Остановка программы...")
        print("=" * 50)
        matrix.Clear()


if __name__ == "__main__":
    main()