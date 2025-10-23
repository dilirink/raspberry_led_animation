#!/usr/bin/env python
# -*- coding: utf-8 -*-
# НАЗВАНИЕ: animation
# ОПИСАНИЕ: 8 эффектов
# https://openprocessing.org/sketch/2421742


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

# ==================== НАСТРОЙКИ ====================
# Параметры LED матрицы
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
CHAIN_LENGTH = 1
PARALLEL = 1
HARDWARE_MAPPING = 'adafruit-hat'

# Параметры анимаций
GLOBAL_SPEED = 0.5  # Общая скорость анимаций
FPS = 30  # Кадров в секунду
FRAME_DELAY = 1.0 / FPS

# Цветовая схема (монохром - белый)
COLOR_FILL = (255, 255, 255)
COLOR_STROKE = (255, 255, 255)

# Режим анимации (выберите один):
# 0 - 3D Sphere Scan
# 1 - Crystalline Refraction
# 2 - Sonar Sweep
# 3 - Helix Scanner
# 4 - Interconnecting Waves
# 5 - Voxel Matrix Morph
# 6 - Phased Array Emitter
# 7 - Crystalline Cube Refraction
# 8 - Auto (переключение каждые 30 секунд)
ANIMATION_MODE = 8

# Время переключения анимаций в авто-режиме (секунды)
AUTO_SWITCH_TIME = 30
# ===================================================


def ease_in_out_cubic(t):
    """Функция плавности для анимаций"""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def get_color_with_opacity(color, opacity):
    """Возвращает цвет с заданной прозрачностью"""
    opacity = max(0, min(1, opacity))
    return tuple(int(c * opacity) for c in color)


class Animation3DSphereScan:
    """3D сфера со сканирующей линией"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = width * 0.35
        self.num_dots = 150
        self.time = 0
        
        # Генерация точек на сфере (распределение Фибоначчи)
        self.dots = []
        for i in range(self.num_dots):
            theta = math.acos(1 - 2 * (i / self.num_dots))
            phi = math.sqrt(self.num_dots * math.pi) * theta
            self.dots.append({
                'x': self.radius * math.sin(theta) * math.cos(phi),
                'y': self.radius * math.sin(theta) * math.sin(phi),
                'z': self.radius * math.cos(theta)
            })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.0005 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Вращение
        rot_x = math.sin(self.time * 0.3) * 0.5
        rot_y = self.time * 0.5
        
        # Сканирующая линия
        eased_time = ease_in_out_cubic((math.sin(self.time * 2.5) + 1) / 2)
        scan_line = (eased_time * 2 - 1) * self.radius
        scan_width = 15
        
        for dot in self.dots:
            x, y, z = dot['x'], dot['y'], dot['z']
            
            # Поворот Y
            nx = x * math.cos(rot_y) - z * math.sin(rot_y)
            nz = x * math.sin(rot_y) + z * math.cos(rot_y)
            x, z = nx, nz
            
            # Поворот X
            ny = y * math.cos(rot_x) - z * math.sin(rot_x)
            nz = y * math.sin(rot_x) + z * math.cos(rot_x)
            y, z = ny, nz
            
            # Проекция
            scale = (z + self.radius * 1.5) / (self.radius * 2.5)
            px = self.center_x + x
            py = self.center_y + y
            
            # Эффект сканирования
            dist_to_scan = abs(y - scan_line)
            scan_influence = math.cos((dist_to_scan / scan_width) * (math.pi / 2)) if dist_to_scan < scan_width else 0
            
            size = max(0, scale * 1.5 + scan_influence * 2)
            opacity = max(0, scale * 0.6 + scan_influence * 0.4)
            
            if size > 0.1:
                color = get_color_with_opacity(COLOR_FILL, opacity)
                draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
        
        return image


class AnimationCrystallineRefraction:
    """Кристаллическая рефракция с волнами"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.grid_size = 10
        self.spacing = width / (self.grid_size - 1)
        self.time = 0
        
        # Генерация точек сетки
        self.dots = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.dots.append({
                    'x': c * self.spacing,
                    'y': r * self.spacing
                })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.16 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        wave_radius = self.time % (self.width * 1.2)
        wave_width = 30
        
        for dot in self.dots:
            dist = math.hypot(dot['x'] - self.center_x, dot['y'] - self.center_y)
            dist_to_wave = abs(dist - wave_radius)
            
            displacement = 0
            if dist_to_wave < wave_width / 2:
                wave_phase = (dist_to_wave / (wave_width / 2)) * math.pi
                displacement = ease_in_out_cubic(math.sin(wave_phase)) * 6
            
            angle_to_center = math.atan2(dot['y'] - self.center_y, dot['x'] - self.center_x)
            dx = math.cos(angle_to_center) * displacement
            dy = math.sin(angle_to_center) * displacement
            
            opacity = 0.2 + (abs(displacement) / 6) * 0.8
            size = 1.0 + (abs(displacement) / 6) * 1.5
            
            px = dot['x'] + dx
            py = dot['y'] + dy
            
            color = get_color_with_opacity(COLOR_FILL, opacity)
            draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
        
        return image


class AnimationSonarSweep:
    """Сонарная развертка"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.time = 0
        self.fade_time = 2500
        
        # Генерация точек на кольцах
        self.rings = []
        for r in range(15, 30, 8):
            for i in range(r):
                angle = (i / r) * math.pi * 2
                self.rings.append({
                    'r': r,
                    'angle': angle,
                    'last_seen': -self.fade_time
                })
    
    def generate_frame(self, delta_time):
        self.time += delta_time
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Луч сканера
        scan_angle = (self.time * 0.001 * (math.pi / 2) * GLOBAL_SPEED) % (math.pi * 2)
        
        # Рисуем луч
        end_x = self.center_x + 30 * math.cos(scan_angle)
        end_y = self.center_y + 30 * math.sin(scan_angle)
        color = get_color_with_opacity(COLOR_STROKE, 0.5)
        draw.line([self.center_x, self.center_y, end_x, end_y], fill=color, width=1)
        
        # Обновление и рисование точек
        for dot in self.rings:
            angle_diff = abs(dot['angle'] - scan_angle)
            if angle_diff > math.pi:
                angle_diff = math.pi * 2 - angle_diff
            
            if angle_diff < 0.1:
                dot['last_seen'] = self.time
            
            time_since_seen = self.time - dot['last_seen']
            if time_since_seen < self.fade_time:
                t = time_since_seen / self.fade_time
                opacity = 1 - ease_in_out_cubic(t)
                size = 1 + opacity * 1.2
                
                x = self.center_x + dot['r'] * math.cos(dot['angle'])
                y = self.center_y + dot['r'] * math.sin(dot['angle'])
                
                color = get_color_with_opacity(COLOR_FILL, opacity)
                draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
        
        return image


class AnimationHelixScanner:
    """Спиральный сканер"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.time = 0
        
        # Генерация точек спирали
        self.points = []
        num_points = 100
        for i in range(num_points):
            t = i / num_points
            angle = t * math.pi * 8
            radius = 5 + t * 20
            y_pos = (t - 0.5) * 40
            self.points.append({
                'x': radius * math.cos(angle),
                'y': y_pos,
                'z': radius * math.sin(angle)
            })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.0008 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        rot_y = self.time * 0.8
        eased_time = ease_in_out_cubic((math.sin(self.time * 3) + 1) / 2)
        scan_line = (eased_time * 2 - 1) * 25
        scan_width = 18
        
        for point in self.points:
            x, y, z = point['x'], point['y'], point['z']
            
            # Поворот Y
            nx = x * math.cos(rot_y) - z * math.sin(rot_y)
            nz = x * math.sin(rot_y) + z * math.cos(rot_y)
            x, z = nx, nz
            
            # Эффект сканирования
            dist_to_scan = abs(y - scan_line)
            scan_influence = math.cos((dist_to_scan / scan_width) * (math.pi / 2)) if dist_to_scan < scan_width else 0
            
            scale = (z + 30) / 60
            px = self.center_x + x
            py = self.center_y + y
            
            size = max(0, scale * 1.5 + scan_influence * 2)
            opacity = max(0.1, scale * 0.6 + scan_influence * 0.4)
            
            if size > 0.1:
                color = get_color_with_opacity(COLOR_FILL, opacity)
                draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
        
        return image


class AnimationInterconnectingWaves:
    """Взаимосвязанные волны"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.time = 0
        
        # Генерация точек сетки
        self.grid_size = 12
        self.spacing = width / (self.grid_size - 1)
        self.points = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.points.append({
                    'x': j * self.spacing,
                    'y': i * self.spacing
                })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.001 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Две волны
        wave1_center_x = self.center_x + math.cos(self.time * 1.2) * 15
        wave1_center_y = self.center_y + math.sin(self.time * 1.2) * 15
        
        wave2_center_x = self.center_x + math.cos(self.time * 1.5 + math.pi) * 12
        wave2_center_y = self.center_y + math.sin(self.time * 1.5 + math.pi) * 12
        
        wave_radius = (self.time * 20) % (self.width * 0.8)
        wave_width = 25
        
        for point in self.points:
            dist1 = math.hypot(point['x'] - wave1_center_x, point['y'] - wave1_center_y)
            dist2 = math.hypot(point['x'] - wave2_center_x, point['y'] - wave2_center_y)
            
            dist_to_wave1 = abs(dist1 - wave_radius)
            dist_to_wave2 = abs(dist2 - wave_radius)
            
            influence1 = math.cos((dist_to_wave1 / wave_width) * math.pi) if dist_to_wave1 < wave_width else 0
            influence2 = math.cos((dist_to_wave2 / wave_width) * math.pi) if dist_to_wave2 < wave_width else 0
            
            combined_influence = max(0, influence1 + influence2)
            
            opacity = 0.15 + combined_influence * 0.85
            size = 0.8 + combined_influence * 1.5
            
            color = get_color_with_opacity(COLOR_FILL, opacity)
            draw.ellipse([point['x'] - size, point['y'] - size, 
                         point['x'] + size, point['y'] + size], fill=color)
        
        return image


class AnimationVoxelMatrixMorph:
    """3D воксельная матрица с морфингом"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.time = 0
        
        # Генерация 3D сетки
        self.grid_size = 6
        self.spacing = 6
        self.points = []
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    self.points.append({
                        'x': (x - (self.grid_size - 1) / 2) * self.spacing,
                        'y': (y - (self.grid_size - 1) / 2) * self.spacing,
                        'z': (z - (self.grid_size - 1) / 2) * self.spacing
                    })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.0005 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        rot_x = self.time * 0.4
        rot_y = self.time * 0.6
        
        eased_time = ease_in_out_cubic((math.sin(self.time * 2) + 1) / 2)
        scan_line = (eased_time * 2 - 1) * 20
        scan_width = 15
        
        points_to_draw = []
        
        for point in self.points:
            x, y, z = point['x'], point['y'], point['z']
            
            # Поворот Y
            nx = x * math.cos(rot_y) - z * math.sin(rot_y)
            nz = x * math.sin(rot_y) + z * math.cos(rot_y)
            x, z = nx, nz
            
            # Поворот X
            ny = y * math.cos(rot_x) - z * math.sin(rot_x)
            nz = y * math.sin(rot_x) + z * math.cos(rot_x)
            y, z = ny, nz
            
            # Эффект сканирования
            dist_to_scan = abs(y - scan_line)
            scan_influence = 0
            displacement = 1
            if dist_to_scan < scan_width:
                scan_influence = math.cos((dist_to_scan / scan_width) * (math.pi / 2))
                displacement = 1 + scan_influence * 0.3
            
            scale = (z + 30) / 60
            px = self.center_x + x * displacement
            py = self.center_y + y * displacement
            
            size = max(0, scale * 1.5 + scan_influence * 1.5)
            opacity = max(0.1, scale * 0.7 + scan_influence * 0.3)
            
            if size > 0.1:
                points_to_draw.append((px, py, z, size, opacity))
        
        # Сортировка по глубине
        points_to_draw.sort(key=lambda p: p[2])
        
        for px, py, z, size, opacity in points_to_draw:
            color = get_color_with_opacity(COLOR_FILL, opacity)
            draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
        
        return image


class AnimationPhasedArrayEmitter:
    """Фазированный массив излучателей"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.time = 0
        
        # Генерация концентрических колец точек
        self.points = []
        ring_radii = [10, 16, 22, 28]
        points_per_ring = [8, 12, 16, 20]
        self.max_radius = ring_radii[-1]
        
        for radius, num_points in zip(ring_radii, points_per_ring):
            for i in range(num_points):
                angle = (i / num_points) * math.pi * 2
                self.points.append({
                    'x': math.cos(angle) * radius,
                    'y': math.sin(angle) * radius,
                    'z': 0
                })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.001 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        rot_x = 1.0
        rot_y = self.time * 0.3
        
        wave_radius = (self.time * 40) % (self.max_radius * 1.5)
        wave_width = 20
        wave_height = 8
        
        points_to_draw = []
        
        for point in self.points:
            x, y, z = point['x'], point['y'], point['z']
            
            # Волновой эффект
            dist_from_center = math.hypot(x, y)
            dist_to_wave = abs(dist_from_center - wave_radius)
            
            wave_influence = 0
            if dist_to_wave < wave_width / 2:
                wave_phase = (1 - dist_to_wave / (wave_width / 2)) * math.pi
                z = ease_in_out_cubic(math.sin(wave_phase)) * wave_height
                wave_influence = z / wave_height
            
            # Поворот Y
            nx = x * math.cos(rot_y) - z * math.sin(rot_y)
            nz = x * math.sin(rot_y) + z * math.cos(rot_y)
            x, z = nx, nz
            
            # Поворот X
            ny = y * math.cos(rot_x) - z * math.sin(rot_x)
            nz = y * math.sin(rot_x) + z * math.cos(rot_x)
            y, z = ny, nz
            
            # Проекция
            fov = 100
            scale = fov / (fov + z + 40)
            px = self.center_x + x * scale
            py = self.center_y + y * scale
            
            size = (1.2 + wave_influence * 2) * scale
            opacity = 0.4 + wave_influence * 0.6
            
            if size > 0.1:
                points_to_draw.append((px, py, z, size, opacity))
        
        # Сортировка по глубине
        points_to_draw.sort(key=lambda p: p[2])
        
        for px, py, z, size, opacity in points_to_draw:
            color = get_color_with_opacity(COLOR_FILL, opacity)
            draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
        
        return image


class AnimationCrystallineCubeRefraction:
    """Кристаллический куб с рефракцией"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.time = 0
        
        # Генерация 3D куба
        self.grid_size = 5
        self.spacing = 8
        cube_half_size = ((self.grid_size - 1) * self.spacing) / 2
        self.max_dist = math.sqrt(3) * cube_half_size
        
        self.points = []
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    self.points.append({
                        'x': x * self.spacing - cube_half_size,
                        'y': y * self.spacing - cube_half_size,
                        'z': z * self.spacing - cube_half_size
                    })
    
    def generate_frame(self, delta_time):
        self.time += delta_time * 0.0003 * GLOBAL_SPEED
        
        image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        rot_x = self.time * 2
        rot_y = self.time * 3
        
        wave_radius = (self.time * 25) % (self.max_dist * 1.3)
        wave_width = 18
        displacement_magnitude = 5
        
        points_to_draw = []
        
        for point in self.points:
            x, y, z = point['x'], point['y'], point['z']
            
            # Волновое смещение от центра
            dist_from_center = math.hypot(x, y, z)
            dist_to_wave = abs(dist_from_center - wave_radius)
            
            displacement_amount = 0
            if dist_to_wave < wave_width / 2:
                wave_phase = (dist_to_wave / (wave_width / 2)) * (math.pi / 2)
                displacement_amount = ease_in_out_cubic(math.cos(wave_phase)) * displacement_magnitude
            
            if displacement_amount > 0 and dist_from_center > 0:
                ratio = (dist_from_center + displacement_amount) / dist_from_center
                x *= ratio
                y *= ratio
                z *= ratio
            
            # Поворот Y
            nx = x * math.cos(rot_y) - z * math.sin(rot_y)
            nz = x * math.sin(rot_y) + z * math.cos(rot_y)
            x, z = nx, nz
            
            # Поворот X
            ny = y * math.cos(rot_x) - z * math.sin(rot_x)
            nz = y * math.sin(rot_x) + z * math.cos(rot_x)
            y, z = ny, nz
            
            # Проекция
            fov = 80
            scale = fov / (fov + z)
            px = self.center_x + x * scale
            py = self.center_y + y * scale
            
            wave_influence = displacement_amount / displacement_magnitude
            size = (1.2 + wave_influence * 2) * scale
            opacity = max(0.1, scale * 0.7 + wave_influence * 0.4)
            
            if size > 0.1:
                points_to_draw.append((px, py, z, size, opacity))
        
        # Сортировка по глубине
        points_to_draw.sort(key=lambda p: p[2])
        
        for px, py, z, size, opacity in points_to_draw:
            color = get_color_with_opacity(COLOR_FILL, opacity)
            draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
        
        return image


# ==================== ГЛАВНАЯ ПРОГРАММА ====================

def main():
    """Основная функция запуска"""
    
    # Инициализация матрицы
    options = RGBMatrixOptions()
    options.rows = MATRIX_HEIGHT
    options.cols = MATRIX_WIDTH
    options.chain_length = CHAIN_LENGTH
    options.parallel = PARALLEL
    options.hardware_mapping = HARDWARE_MAPPING
    
    matrix = RGBMatrix(options=options)
    
    # Создание всех анимаций
    animations = [
        Animation3DSphereScan(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationCrystallineRefraction(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationSonarSweep(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationHelixScanner(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationInterconnectingWaves(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationVoxelMatrixMorph(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationPhasedArrayEmitter(MATRIX_WIDTH, MATRIX_HEIGHT),
        AnimationCrystallineCubeRefraction(MATRIX_WIDTH, MATRIX_HEIGHT)
    ]
    
    animation_names = [
        "3D Sphere Scan",
        "Crystalline Refraction",
        "Sonar Sweep",
        "Helix Scanner",
        "Interconnecting Waves",
        "Voxel Matrix Morph",
        "Phased Array Emitter",
        "Crystalline Cube Refraction"
    ]
    
    # Выбор начальной анимации
    if ANIMATION_MODE == 8:
        # Создаем случайный порядок анимаций
        animation_order = list(range(len(animations)))
        random.shuffle(animation_order)
        current_animation_index = 0
        current_animation = animation_order[current_animation_index]
        auto_mode = True
        print("Режим автопереключения анимаций (случайный порядок)")
        print(f"Порядок воспроизведения: {[animation_names[i] for i in animation_order]}")
    else:
        current_animation = ANIMATION_MODE
        current_animation_index = 0
        animation_order = None
        auto_mode = False
        print(f"Запуск анимации: {animation_names[current_animation]}")
    
    last_switch_time = time.time()
    last_time = time.time()
    
    try:
        print("Нажмите CTRL-C для остановки.")
        
        while True:
            current_time = time.time()
            delta_time = (current_time - last_time) * 1000  # миллисекунды
            last_time = current_time
            
            # Автопереключение анимаций
            if auto_mode and (current_time - last_switch_time) >= AUTO_SWITCH_TIME:
                current_animation_index = (current_animation_index + 1) % len(animations)
                current_animation = animation_order[current_animation_index]
                last_switch_time = current_time
                print(f"Переключение на: {animation_names[current_animation]}")
            
            # Генерация кадра
            frame = animations[current_animation].generate_frame(delta_time)
            
            # Отображение на матрице
            matrix.SetImage(frame.convert("RGB"))
            
            # Задержка для поддержания FPS
            time.sleep(FRAME_DELAY)
            
    except KeyboardInterrupt:
        print("\nОстановка...")
        matrix.Clear()


if __name__ == "__main__":
    main()