#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Красивый вывод текста на LED панель 64x64 с эффектами
"""

import sys
import time
import argparse
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

# ========== НАСТРОЙКИ ==========
MATRIX_ROWS = 64
MATRIX_COLS = 64
CHAIN_LENGTH = 1
PARALLEL = 1
HARDWARE_MAPPING = 'regular'

# Цветовые схемы
COLOR_SCHEMES = {
    'blue': {
        'glow': (0, 50, 100),
        'main': (0, 200, 255),
        'background': (0, 0, 0)
    },
    'green': {
        'glow': (0, 50, 0),
        'main': (0, 255, 0),
        'background': (0, 0, 0)
    },
    'red': {
        'glow': (50, 0, 0),
        'main': (255, 0, 0),
        'background': (0, 0, 0)
    },
    'purple': {
        'glow': (50, 0, 50),
        'main': (255, 0, 255),
        'background': (0, 0, 0)
    },
    'yellow': {
        'glow': (50, 50, 0),
        'main': (255, 255, 0),
        'background': (0, 0, 0)
    },
    'cyan': {
        'glow': (0, 50, 50),
        'main': (0, 255, 255),
        'background': (0, 0, 0)
    },
    'white': {
        'glow': (50, 50, 50),
        'main': (255, 255, 255),
        'background': (0, 0, 0)
    }
}
# ==============================


class TextDisplay:
    """Класс для отображения текста на LED матрице"""
    
    def __init__(self, matrix, color_scheme='blue'):
        self.matrix = matrix
        self.width = MATRIX_COLS
        self.height = MATRIX_ROWS
        self.colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES['blue'])
        
    def get_font(self, size=10):
        """Получение шрифта с указанным размером"""
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            try:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
            except:
                return ImageFont.load_default()
    
    def display_text(self, text, duration=0, font_size=10, glow=True):
        """
        Отображение текста на матрице
        
        Args:
            text: Текст для отображения (можно использовать \n для переноса строк)
            duration: Время отображения в секундах (0 = бесконечно)
            font_size: Размер шрифта
            glow: Применять ли эффект свечения
        """
        image = Image.new("RGB", (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(image)
        
        font = self.get_font(font_size)
        lines = text.split('\n')
        
        # Вычисляем высоту каждой строки
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
            line_widths.append(bbox[2] - bbox[0])
        
        # Общая высота текста с отступами между строками
        spacing = 2
        total_height = sum(line_heights) + spacing * (len(lines) - 1)
        y_offset = (self.height - total_height) // 2
        
        # Рисуем каждую строку
        for i, line in enumerate(lines):
            text_width = line_widths[i]
            text_height = line_heights[i]
            
            # Центрируем по горизонтали
            x = (self.width - text_width) // 2
            y = y_offset
            
            # Эффект свечения (рисуем текст с небольшим смещением)
            if glow:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), line, font=font, 
                                    fill=self.colors['glow'])
            
            # Основной текст
            draw.text((x, y), line, font=font, fill=self.colors['main'])
            
            y_offset += text_height + spacing
        
        # Отображаем на матрице
        self.matrix.SetImage(image.convert("RGB"))
        
        if duration > 0:
            time.sleep(duration)
    
    def display_scrolling_text(self, text, font_size=10, speed=0.05):
        """
        Горизонтальная прокрутка текста (бегущая строка)
        
        Args:
            text: Текст для прокрутки
            font_size: Размер шрифта
            speed: Скорость прокрутки (секунды между кадрами)
        """
        font = self.get_font(font_size)
        
        # Создаем временное изображение для измерения ширины текста
        temp_image = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_image)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Вертикальное позиционирование
        y = (self.height - text_height) // 2
        
        # Начинаем справа от экрана и двигаем влево
        for x_pos in range(self.width, -text_width - 10, -1):
            image = Image.new("RGB", (self.width, self.height), 
                            self.colors['background'])
            draw = ImageDraw.Draw(image)
            
            # Эффект свечения
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((x_pos + dx, y + dy), text, font=font, 
                                fill=self.colors['glow'])
            
            # Основной текст
            draw.text((x_pos, y), text, font=font, fill=self.colors['main'])
            
            self.matrix.SetImage(image.convert("RGB"))
            time.sleep(speed)


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Отображение текста на LED матрице 64x64',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s "Привет мир"
  %(prog)s "Первая строка\\nВторая строка" --color green
  %(prog)s "Бегущая строка" --scroll --speed 0.03
  %(prog)s "HELLO\\nWORLD" --duration 10 --size 12
        """
    )
    
    parser.add_argument('text', type=str, help='Текст для отображения (используйте \\n для переноса строк)')
    parser.add_argument('-d', '--duration', type=float, default=0,
                       help='Время отображения в секундах (0 = бесконечно, по умолчанию: 0)')
    parser.add_argument('-s', '--size', type=int, default=10,
                       help='Размер шрифта (по умолчанию: 10)')
    parser.add_argument('-c', '--color', choices=COLOR_SCHEMES.keys(), default='blue',
                       help='Цветовая схема (по умолчанию: blue)')
    parser.add_argument('--scroll', action='store_true',
                       help='Режим бегущей строки (горизонтальная прокрутка)')
    parser.add_argument('--speed', type=float, default=0.05,
                       help='Скорость прокрутки в секундах (по умолчанию: 0.05)')
    parser.add_argument('--no-glow', action='store_true',
                       help='Отключить эффект свечения')
    
    args = parser.parse_args()
    
    # Обрабатываем escape-последовательности в тексте
    args.text = args.text.replace('\\n', '\n').replace('\\t', '\t')
    
    # Инициализация матрицы
    options = RGBMatrixOptions()
    options.rows = MATRIX_ROWS
    options.cols = MATRIX_COLS
    options.chain_length = CHAIN_LENGTH
    options.parallel = PARALLEL
    options.hardware_mapping = HARDWARE_MAPPING
    
    matrix = RGBMatrix(options=options)
    display = TextDisplay(matrix, color_scheme=args.color)
    
    try:
        print("=" * 60)
        print("LED Matrix Text Display")
        print("=" * 60)
        print(f"Текст: {args.text}")
        print(f"Цвет: {args.color}")
        print(f"Размер шрифта: {args.size}")
        if args.scroll:
            print(f"Режим: Бегущая строка (скорость: {args.speed}s)")
        else:
            print(f"Режим: Статический (длительность: {args.duration}s)")
        print("Нажмите CTRL-C для остановки")
        print("=" * 60)
        
        if args.scroll:
            # Бесконечная прокрутка
            while True:
                display.display_scrolling_text(args.text, 
                                              font_size=args.size,
                                              speed=args.speed)
        else:
            # Статическое отображение
            display.display_text(args.text, 
                               duration=args.duration,
                               font_size=args.size,
                               glow=not args.no_glow)
            
            # Если duration = 0, держим бесконечно
            if args.duration == 0:
                while True:
                    time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Остановка программы...")
        print("=" * 60)
        matrix.Clear()


if __name__ == "__main__":
    main()