#!/usr/bin/env python
import time
import random
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw, ImageFilter
try:
    from noise import pnoise3
except ImportError:
    print("Installing noise library...")
    import subprocess
    subprocess.check_call(["pip", "install", "noise", "--break-system-packages"])
    from noise import pnoise3

# ============================================
# НАСТРОЙКИ
# ============================================
# Настройки матрицы
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
MATRIX_CHAIN_LENGTH = 1
MATRIX_PARALLEL = 1
MATRIX_HARDWARE_MAPPING = 'regular'

# Настройки анимации
OBJECTS_NUM = 25  # Количество линий
FRAME_RATE = 60  # FPS
FRAME_DELAY = 1.0 / FRAME_RATE

# Палитра цветов
PALETTE = [
    "#FF00D8",
    "#FFB201",
    "#98FF00",
    "#00FFC4",
    "#0082FE",
    "#B733FF",
]

# Фон
BACKGROUND_COLOR = "#000000"

# Параметры линий
RANGE_X_OPTIONS = [5, 5, 5, 5, 5, 5, 10, 10, 10, 20, 20, 30, 30, 30, 30, 40, 50]
LINE_WIDTH_MIN = 1  # Увеличено для объема
LINE_WIDTH_MAX = 3  # Увеличено для объема
BASE_ALPHA = 80  # Базовая прозрачность (ниже = прозрачнее)
ALPHA_SHORT_LINES = 50  # Прозрачность для коротких линий
GLOW_LAYERS = 3  # Количество слоев свечения для объема
OUT_PROBABILITY = 10

# ============================================
# ИНИЦИАЛИЗАЦИЯ МАТРИЦЫ
# ============================================
options = RGBMatrixOptions()
options.rows = MATRIX_HEIGHT
options.cols = MATRIX_WIDTH
options.chain_length = MATRIX_CHAIN_LENGTH
options.parallel = MATRIX_PARALLEL
options.hardware_mapping = MATRIX_HARDWARE_MAPPING

matrix = RGBMatrix(options=options)

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================
def hex_to_rgb(hex_color):
    """Конвертирует HEX цвет в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def map_value(value, in_min, in_max, out_min, out_max):
    """Аналог map() из p5.js"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# ============================================
# КЛАСС ОБЪЕКТА (ЛИНИИ)
# ============================================
class Obj:
    def __init__(self, index):
        self.index = index
        self.start_x = random.uniform(0, MATRIX_WIDTH)
        self.frame_count = 0
        self.init()
        self.goal_x = self.start_x + self.range_x
    
    def init(self):
        """Инициализация параметров линии"""
        self.range_x = random.choice(RANGE_X_OPTIONS)
        self.step = map_value(self.range_x, 5, 50, 2, 10)
        self.str_weight = random.uniform(LINE_WIDTH_MIN, LINE_WIDTH_MAX)
        self.color = hex_to_rgb(random.choice(PALETTE))
        
        # Альфа канал для коротких линий - больше прозрачности
        if self.range_x < 30:
            self.alpha = ALPHA_SHORT_LINES
        else:
            self.alpha = BASE_ALPHA
            
        self.is_out = random.random() * 100 < OUT_PROBABILITY
    
    def move(self):
        """Движение линии"""
        self.start_x += self.step
        self.goal_x = self.start_x + self.range_x
        
        # Если линия ушла за границу, переинициализируем
        if self.start_x > MATRIX_WIDTH:
            self.init()
            self.start_x = -self.range_x
            self.goal_x = self.start_x + self.range_x
    
    def get_points(self, frame_count):
        """Генерирует точки для линии с использованием Perlin noise"""
        points = []
        x = self.start_x
        while x <= self.goal_x:
            if 0 <= x < MATRIX_WIDTH:
                # Perlin noise для волнообразного движения
                noise_scale = 0.025 if self.is_out else 0.005
                noise_val = pnoise3(
                    x * 0.05,
                    self.index * noise_scale,
                    frame_count * 0.01,
                    octaves=2
                )
                
                # Нормализуем noise от [-1, 1] к [0, 1]
                noise_val = (noise_val + 1) / 2
                
                # Маппим на высоту экрана
                y = map_value(
                    noise_val,
                    0, 1,
                    -MATRIX_HEIGHT * 0.25,
                    MATRIX_HEIGHT * 1.25
                )
                
                points.append((x, y))
            x += 1
        
        return points

# ============================================
# ГЕНЕРАЦИЯ КАДРА
# ============================================
def generate_frame(objects, frame_count):
    """Генерирует один кадр анимации с объемными линиями"""
    # Создаем изображение с альфа-каналом
    img = Image.new('RGBA', (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0, 0))
    
    # Рисуем каждый объект со слоями для объема
    for obj in objects:
        points = obj.get_points(frame_count)
        
        if len(points) > 1:
            # Создаем временный слой для этой линии
            layer = Image.new('RGBA', (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            
            # Рисуем несколько слоев с разной толщиной и прозрачностью для объема
            for glow_layer in range(GLOW_LAYERS, 0, -1):
                # Вычисляем параметры для каждого слоя
                layer_width = int(obj.str_weight * (1 + glow_layer * 0.5))
                layer_alpha = int(obj.alpha * (0.3 + 0.7 / glow_layer))
                
                color = obj.color + (layer_alpha,)
                
                # Рисуем линию по точкам
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    draw.line([(x1, y1), (x2, y2)], fill=color, width=layer_width)
            
            # Добавляем легкое размытие для мягкости
            layer = layer.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Накладываем слой на основное изображение
            img = Image.alpha_composite(img, layer)
    
    # Создаем финальное изображение с фоном
    background = Image.new('RGB', (MATRIX_WIDTH, MATRIX_HEIGHT), hex_to_rgb(BACKGROUND_COLOR))
    
    # Накладываем все линии на фон
    background.paste(img, (0, 0), img)
    
    return background

# ============================================
# ГЛАВНЫЙ ЦИКЛ
# ============================================
def main():
    # Инициализация объектов
    objs = []
    for i in range(OBJECTS_NUM):
        objs.append(Obj(i))
    
    frame_count = 0
    
    try:
        print(f"Starting animation on {MATRIX_WIDTH}x{MATRIX_HEIGHT} LED matrix")
        print("Press CTRL-C to stop.")
        
        while True:
            # Двигаем все объекты
            for obj in objs:
                obj.move()
            
            # Генерируем кадр
            frame = generate_frame(objs, frame_count)
            
            # Отображаем на матрице
            matrix.SetImage(frame)
            
            # Обновляем счетчик кадров
            frame_count += 1
            
            # Задержка для соблюдения FPS
            time.sleep(FRAME_DELAY)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        matrix.Clear()

if __name__ == "__main__":
    main()

