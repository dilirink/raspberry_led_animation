#!/usr/bin/env python
# НАЗВАНИЕ: Пересечение фигур
# ОПИСАНИЕ: Движущиеся геометрические фигуры с подсветкой точек пересечения
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



# ============= НАСТРОЙКИ =============
# Параметры матрицы
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64

# Параметры фигур
NUM_SHAPES = 6  # Количество фигур
SHAPE_TYPES = ["circle", "line", "rectangle", "square"]  # Типы фигур
MIN_RADIUS = 5  # Минимальный радиус окружности
MAX_RADIUS = 15  # Максимальный радиус окружности
LINE_LENGTH_MIN = 10  # Минимальная длина линии
LINE_LENGTH_MAX = 25  # Максимальная длина линии
RECT_WIDTH_MIN = 8  # Минимальная ширина прямоугольника
RECT_WIDTH_MAX = 20  # Максимальная ширина прямоугольника
RECT_HEIGHT_MIN = 8  # Минимальная высота прямоугольника
RECT_HEIGHT_MAX = 20  # Максимальная высота прямоугольника
SQUARE_SIZE_MIN = 8  # Минимальный размер квадрата
SQUARE_SIZE_MAX = 18  # Максимальный размер квадрата

# Параметры движения
SPEED_MIN = 0.3  # Минимальная скорость
SPEED_MAX = 1.0  # Максимальная скорость
FPS = 30  # Частота обновления кадров

# Цвета
SHAPE_COLOR = (255, 255, 255)  # Белый цвет фигур
INTERSECTION_COLOR = (255, 0, 0)  # Красный цвет пересечений
BACKGROUND_COLOR = (0, 0, 0)  # Черный фон
# =====================================

# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = MATRIX_HEIGHT
options.cols = MATRIX_WIDTH
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

class Shape:
    def __init__(self, shape_type):
        self.type = shape_type
        self.x = random.uniform(0, MATRIX_WIDTH)
        self.y = random.uniform(0, MATRIX_HEIGHT)
        self.vx = random.uniform(SPEED_MIN, SPEED_MAX) * random.choice([-1, 1])
        self.vy = random.uniform(SPEED_MIN, SPEED_MAX) * random.choice([-1, 1])
        
        if shape_type == "circle":
            self.radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
        elif shape_type == "line":
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(LINE_LENGTH_MIN, LINE_LENGTH_MAX)
            self.x2_offset = length * math.cos(angle)
            self.y2_offset = length * math.sin(angle)
        elif shape_type == "rectangle":
            self.width = random.uniform(RECT_WIDTH_MIN, RECT_WIDTH_MAX)
            self.height = random.uniform(RECT_HEIGHT_MIN, RECT_HEIGHT_MAX)
        elif shape_type == "square":
            self.size = random.uniform(SQUARE_SIZE_MIN, SQUARE_SIZE_MAX)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Отражение от границ
        if self.type == "circle":
            if self.x - self.radius < 0 or self.x + self.radius > MATRIX_WIDTH:
                self.vx *= -1
                self.x = max(self.radius, min(MATRIX_WIDTH - self.radius, self.x))
            if self.y - self.radius < 0 or self.y + self.radius > MATRIX_HEIGHT:
                self.vy *= -1
                self.y = max(self.radius, min(MATRIX_HEIGHT - self.radius, self.y))
        elif self.type == "line":
            if self.x < 0 or self.x > MATRIX_WIDTH or \
               self.x + self.x2_offset < 0 or self.x + self.x2_offset > MATRIX_WIDTH:
                self.vx *= -1
            if self.y < 0 or self.y > MATRIX_HEIGHT or \
               self.y + self.y2_offset < 0 or self.y + self.y2_offset > MATRIX_HEIGHT:
                self.vy *= -1
        elif self.type == "rectangle":
            if self.x < 0 or self.x + self.width > MATRIX_WIDTH:
                self.vx *= -1
                self.x = max(0, min(MATRIX_WIDTH - self.width, self.x))
            if self.y < 0 or self.y + self.height > MATRIX_HEIGHT:
                self.vy *= -1
                self.y = max(0, min(MATRIX_HEIGHT - self.height, self.y))
        elif self.type == "square":
            if self.x < 0 or self.x + self.size > MATRIX_WIDTH:
                self.vx *= -1
                self.x = max(0, min(MATRIX_WIDTH - self.size, self.x))
            if self.y < 0 or self.y + self.size > MATRIX_HEIGHT:
                self.vy *= -1
                self.y = max(0, min(MATRIX_HEIGHT - self.size, self.y))
    
    def get_points(self, num_points=36):
        """Возвращает точки фигуры для проверки пересечений"""
        points = []
        if self.type == "circle":
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                px = self.x + self.radius * math.cos(angle)
                py = self.y + self.radius * math.sin(angle)
                points.append((px, py))
        elif self.type == "line":
            x2 = self.x + self.x2_offset
            y2 = self.y + self.y2_offset
            for i in range(num_points):
                t = i / (num_points - 1)
                px = self.x + t * (x2 - self.x)
                py = self.y + t * (y2 - self.y)
                points.append((px, py))
        elif self.type == "rectangle":
            # Периметр прямоугольника
            points_per_side = num_points // 4
            # Верхняя сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x + t * self.width, self.y))
            # Правая сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x + self.width, self.y + t * self.height))
            # Нижняя сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x + self.width - t * self.width, self.y + self.height))
            # Левая сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x, self.y + self.height - t * self.height))
        elif self.type == "square":
            # Периметр квадрата
            points_per_side = num_points // 4
            # Верхняя сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x + t * self.size, self.y))
            # Правая сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x + self.size, self.y + t * self.size))
            # Нижняя сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x + self.size - t * self.size, self.y + self.size))
            # Левая сторона
            for i in range(points_per_side):
                t = i / points_per_side
                points.append((self.x, self.y + self.size - t * self.size))
        return points

def point_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def find_intersections(shapes):
    """Находит точки пересечения фигур"""
    intersections = []
    threshold = 1.5  # Порог для определения пересечения
    
    for i in range(len(shapes)):
        points_i = shapes[i].get_points()
        for j in range(i + 1, len(shapes)):
            points_j = shapes[j].get_points()
            
            # Проверяем близость точек между двумя фигурами
            for pi in points_i:
                for pj in points_j:
                    if point_distance(pi, pj) < threshold:
                        # Добавляем среднюю точку как пересечение
                        intersections.append(((pi[0] + pj[0]) / 2, (pi[1] + pj[1]) / 2))
    
    return intersections

# Создание фигур
shapes = [Shape(random.choice(SHAPE_TYPES)) for _ in range(NUM_SHAPES)]

try:
    print("Press CTRL-C to stop.")
    while True:
        # Обновление позиций
        for shape in shapes:
            shape.update()
        
        # Создание изображения
        image = Image.new("RGB", (MATRIX_WIDTH, MATRIX_HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)
        
        # Рисование фигур
        for shape in shapes:
            if shape.type == "circle":
                x1 = shape.x - shape.radius
                y1 = shape.y - shape.radius
                x2 = shape.x + shape.radius
                y2 = shape.y + shape.radius
                draw.ellipse([x1, y1, x2, y2], outline=SHAPE_COLOR, width=1)
            elif shape.type == "line":
                x2 = shape.x + shape.x2_offset
                y2 = shape.y + shape.y2_offset
                draw.line([shape.x, shape.y, x2, y2], fill=SHAPE_COLOR, width=1)
            elif shape.type == "rectangle":
                x1 = shape.x
                y1 = shape.y
                x2 = shape.x + shape.width
                y2 = shape.y + shape.height
                draw.rectangle([x1, y1, x2, y2], outline=SHAPE_COLOR, width=1)
            elif shape.type == "square":
                x1 = shape.x
                y1 = shape.y
                x2 = shape.x + shape.size
                y2 = shape.y + shape.size
                draw.rectangle([x1, y1, x2, y2], outline=SHAPE_COLOR, width=1)
        
        # Поиск и отрисовка пересечений
        intersections = find_intersections(shapes)
        for ix, iy in intersections:
            # Рисуем точку пересечения (маленький круг)
            draw.ellipse([ix-1, iy-1, ix+1, iy+1], fill=INTERSECTION_COLOR)
        
        matrix.SetImage(image.convert("RGB"))
        time.sleep(1.0 / FPS)
        
except KeyboardInterrupt:
    print("Exiting...")