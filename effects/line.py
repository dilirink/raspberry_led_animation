#!/usr/bin/env python
import time
import random
import math
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw

# ============ НАСТРОЙКИ МАТРИЦЫ ============
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
CHAIN_LENGTH = 1
PARALLEL = 1
HARDWARE_MAPPING = 'adafruit-hat'

# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = MATRIX_HEIGHT
options.cols = MATRIX_WIDTH
options.chain_length = CHAIN_LENGTH
options.parallel = PARALLEL
options.hardware_mapping = HARDWARE_MAPPING

matrix = RGBMatrix(options=options)


# ============================================
# ЭФФЕКТ 2: RGB ЛИНИИ
# ============================================
class RGBLinesEffect:
    def __init__(self):
        self.name = "RGB линии"
        self.line_positions = [32.0, 32.0, 32.0]
        self.line_velocities = [0.0, 0.0, 0.0]
        self.target_velocities = [0.0, 0.0, 0.0]
        self.state = "starting"
        self.state_timer = 0

        # Рандомизация параметров
        self.speed = random.uniform(0.3, 0.8)
        self.start_delay = random.uniform(1, 3)
        self.disperse_time = random.uniform(15, 25)
        self.return_time = random.uniform(2, 4)
        self.velocity_smoothing = random.uniform(0.15, 0.35)

        self.line_colors = [
            (random.randint(200, 255), 0, 0),
            (0, random.randint(200, 255), 0),
            (0, 0, random.randint(200, 255))
        ]

    def generate_frame(self):
        self.state_timer += 1.0 / 60

        # Переключение состояний
        if self.state == "starting" and self.state_timer >= self.start_delay:
            self.state = "dispersing"
            self.state_timer = 0
        elif self.state == "dispersing" and self.state_timer >= self.disperse_time:
            self.state = "returning"
            self.state_timer = 0
        elif self.state == "returning" and self.state_timer >= self.return_time:
            return None  # Эффект завершен

        image = Image.new("RGB", (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0))
        pixels = image.load()

        if self.state == "dispersing":
            for i in range(len(self.line_positions)):
                if random.random() < 0.05:
                    self.target_velocities[i] = random.uniform(-self.speed, self.speed)

                diff = self.target_velocities[i] - self.line_velocities[i]
                self.line_velocities[i] += diff * self.velocity_smoothing

                self.line_positions[i] += self.line_velocities[i]

                if self.line_positions[i] < 0:
                    self.line_positions[i] = 0
                    self.target_velocities[i] = abs(self.target_velocities[i])
                elif self.line_positions[i] >= MATRIX_HEIGHT:
                    self.line_positions[i] = MATRIX_HEIGHT - 1
                    self.target_velocities[i] = -abs(self.target_velocities[i])

        elif self.state == "returning":
            for i in range(len(self.line_positions)):
                diff = 32 - self.line_positions[i]
                if abs(diff) > 0.1:
                    self.line_positions[i] += diff * 0.1
                else:
                    self.line_positions[i] = 32

        # Рисуем линии
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                r, g, b = 0, 0, 0

                for i, (pos, color) in enumerate(zip(self.line_positions, self.line_colors)):
                    if int(pos) <= y < int(pos) + 1:
                        r += color[0]
                        g += color[1]
                        b += color[2]

                r = min(255, r)
                g = min(255, g)
                b = min(255, b)

                if r > 0 or g > 0 or b > 0:
                    pixels[x, y] = (r, g, b)

        return image

# ============================================
# ЭФФЕКТ 3: ВРАЩАЮЩАЯСЯ ЛИНИЯ
# ============================================
class RotatingLineEffect:
    def __init__(self):
        self.name = "Вращающаяся линия"
        self.angle = 0

        # Рандомизация
        self.static_duration = random.uniform(2, 4)
        self.rotation_duration = random.uniform(15, 25)
        self.rotation_speed = 360.0 / self.rotation_duration
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

        self.elapsed = 0

    def generate_frame(self):
        self.elapsed += 1.0 / 60

        if self.elapsed >= self.static_duration + self.rotation_duration:
            return None  # Эффект завершен

        image = Image.new("RGB", (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        if self.elapsed < self.static_duration:
            angle_degrees = 0
        else:
            rotation_progress = (self.elapsed - self.static_duration) / self.rotation_duration
            angle_degrees = rotation_progress * 360

        angle_rad = math.radians(angle_degrees)
        half_length = MATRIX_WIDTH / 2

        x1 = MATRIX_WIDTH/2 - half_length * math.cos(angle_rad)
        y1 = MATRIX_HEIGHT/2 - half_length * math.sin(angle_rad)
        x2 = MATRIX_WIDTH/2 + half_length * math.cos(angle_rad)
        y2 = MATRIX_HEIGHT/2 + half_length * math.sin(angle_rad)

        draw.line([(x1, y1), (x2, y2)], fill=self.color, width=1)

        return image

# ============================================
# ЭФФЕКТ 4: МЕНЯЮЩИЙСЯ КВАДРАТ
# ============================================
class ChangingSquareEffect:
    def __init__(self):
        self.name = "Меняющийся квадрат"
        self.current_width = 64.0
        self.current_height = 0.0
        self.target_width = 64.0
        self.target_height = 0.0
        self.change_counter = 0
        self.last_change_time = 0

        # Рандомизация
        self.change_speed = random.uniform(0.2, 0.4)
        self.change_interval = random.uniform(1.5, 3.0)
        self.number_of_changes = random.randint(6, 10)
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    def get_next_target_size(self):
        self.change_counter += 1

        if self.change_counter > self.number_of_changes:
            return None  # Эффект завершен

        change_dimension = random.choice(['width', 'height'])

        if change_dimension == 'width':
            new_width = random.randint(10, 64)
            return new_width, self.target_height
        else:
            new_height = random.randint(0, 50)
            return self.target_width, new_height

    def generate_frame(self):
        self.last_change_time += 1.0 / 60

        if self.last_change_time >= self.change_interval:
            if abs(self.current_width - self.target_width) < 1 and abs(self.current_height - self.target_height) < 1:
                result = self.get_next_target_size()
                if result is None:
                    return None  # Эффект завершен
                self.target_width, self.target_height = result
                self.last_change_time = 0

        img = Image.new("RGB", (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Плавное движение к целевым размерам
        diff_w = self.target_width - self.current_width
        if abs(diff_w) < 0.1:
            self.current_width = self.target_width
        else:
            self.current_width += diff_w * self.change_speed

        diff_h = self.target_height - self.current_height
        if abs(diff_h) < 0.1:
            self.current_height = self.target_height
        else:
            self.current_height += diff_h * self.change_speed

        x1 = (MATRIX_WIDTH - self.current_width) / 2
        y1 = (MATRIX_HEIGHT - self.current_height) / 2
        x2 = x1 + self.current_width - 1
        y2 = y1 + self.current_height - 1

        if self.current_height > 1:
            draw.rectangle([x1, y1, x2, y2], outline=self.color, width=1)
        else:
            draw.line([(x1, MATRIX_HEIGHT // 2), (x2, MATRIX_HEIGHT // 2)], fill=self.color, width=1)

        return img

# ============================================
# ЭФФЕКТ 5: ТРИ СИНУСОИДЫ
# ============================================
class ThreeSinesEffect:
    def __init__(self):
        self.name = "Три синусоиды"
        self.elapsed = 0

        # Рандомизация
        self.sine_amplitude = random.randint(10, 15)
        self.sine_frequency = random.uniform(1.5, 2.5)
        self.sine_speed = random.uniform(1.5, 2.5)
        self.amplitude_rise_time = random.uniform(1.5, 2.5)
        self.amplitude_fall_time = random.uniform(1.5, 2.5)
        self.sine_duration = random.uniform(18, 22)

        self.color_sine_1 = (random.randint(200, 255), random.randint(150, 200), random.randint(150, 200))
        self.color_sine_2 = (random.randint(150, 200), random.randint(200, 255), random.randint(150, 200))
        self.color_sine_3 = (random.randint(150, 200), random.randint(150, 200), random.randint(200, 255))

    def calculate_amplitude(self, sine_time):
        if sine_time < self.amplitude_rise_time:
            return self.sine_amplitude * (sine_time / self.amplitude_rise_time)
        elif sine_time > self.sine_duration - self.amplitude_fall_time:
            remaining_time = self.sine_duration - sine_time
            return self.sine_amplitude * (remaining_time / self.amplitude_fall_time)
        else:
            return self.sine_amplitude

    def draw_sine_wave(self, draw, y_center, phase, amplitude, time_offset, color):
        points = []
        for x in range(MATRIX_WIDTH):
            y = y_center + amplitude * math.sin(2 * math.pi * self.sine_frequency * x / MATRIX_WIDTH + phase + time_offset)
            y = int(max(0, min(MATRIX_HEIGHT - 1, y)))
            points.append((x, y))

        if len(points) > 1:
            draw.line(points, fill=color, width=1)

    def generate_frame(self):
        self.elapsed += 1.0 / 60

        if self.elapsed >= 4 + self.sine_duration + 1:
            return None  # Эффект завершен

        image = Image.new("RGB", (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        center_y = MATRIX_HEIGHT / 2.0

        if self.elapsed < 3:
            # Одна линия
            draw.line([(0, int(center_y)), (MATRIX_WIDTH - 1, int(center_y))], fill=(255, 255, 255), width=1)
        elif self.elapsed < 4:
            # Разделение на 5 линий
            progress = (self.elapsed - 3) / 1.0
            border_distance = self.sine_amplitude + 2

            target_positions = [
                center_y - border_distance,
                center_y,
                center_y,
                center_y,
                center_y + border_distance
            ]

            for target_y in target_positions:
                current_y = center_y + (target_y - center_y) * progress
                draw.line([(0, int(current_y)), (MATRIX_WIDTH - 1, int(current_y))], fill=(255, 255, 255), width=1)
        elif self.elapsed < 4 + self.sine_duration:
            # Синусоиды
            sine_time = self.elapsed - 4
            time_offset = sine_time * self.sine_speed
            amplitude = self.calculate_amplitude(sine_time)

            border_distance = amplitude + 2
            upper_border_y = int(center_y - border_distance)
            lower_border_y = int(center_y + border_distance)
            draw.line([(0, upper_border_y), (MATRIX_WIDTH - 1, upper_border_y)], fill=(255, 255, 255), width=1)
            draw.line([(0, lower_border_y), (MATRIX_WIDTH - 1, lower_border_y)], fill=(255, 255, 255), width=1)

            phase_shift = 2 * math.pi / 3
            self.draw_sine_wave(draw, center_y, 0, amplitude, time_offset, self.color_sine_1)
            self.draw_sine_wave(draw, center_y, phase_shift, amplitude, time_offset, self.color_sine_2)
            self.draw_sine_wave(draw, center_y, 2 * phase_shift, amplitude, time_offset, self.color_sine_3)
        else:
            # Возврат в линию
            progress = 1.0 - (self.elapsed - 4 - self.sine_duration) / 1.0
            border_distance = self.sine_amplitude + 2

            positions = [
                center_y - border_distance,
                center_y,
                center_y,
                center_y,
                center_y + border_distance
            ]

            for pos_y in positions:
                current_y = center_y + (pos_y - center_y) * progress
                draw.line([(0, int(current_y)), (MATRIX_WIDTH - 1, int(current_y))], fill=(255, 255, 255), width=1)

        return image

# ============================================
# ЭФФЕКТ 6: ГРАВИТАЦИЯ (РАЗЛЕТ И СБОРКА)
# ============================================
class GravityEffect:
    def __init__(self):
        self.name = "Гравитация"
        self.elapsed = 0

        # Рандомизация
        self.spread_duration = random.uniform(18, 22)
        self.gather_duration = random.uniform(18, 22)
        self.num_particles = 64
        self.gravity_strength = random.uniform(0.3, 0.7)
        self.damping = random.uniform(0.96, 0.99)
        self.spread_force = random.uniform(1.5, 2.5)
        self.gather_force = random.uniform(2.5, 3.5)

        self.particles = []
        for i in range(self.num_particles):
            self.particles.append(self.Particle(i, MATRIX_HEIGHT // 2))

    class Particle:
        def __init__(self, x, y):
            self.x = float(x)
            self.y = float(y)
            self.vx = 0.0
            self.vy = 0.0

        def apply_force(self, fx, fy):
            self.vx += fx
            self.vy += fy

        def update(self, damping):
            self.vx *= damping
            self.vy *= damping
            self.x += self.vx
            self.y += self.vy

            if self.x < 0:
                self.x = 0
                self.vx *= -0.5
            elif self.x >= MATRIX_WIDTH:
                self.x = MATRIX_WIDTH - 1
                self.vx *= -0.5

            if self.y < 0:
                self.y = 0
                self.vy *= -0.5
            elif self.y >= MATRIX_HEIGHT:
                self.y = MATRIX_HEIGHT - 1
                self.vy *= -0.5

    def generate_frame(self):
        self.elapsed += 1.0 / 60

        if self.elapsed >= self.spread_duration + self.gather_duration:
            return None  # Эффект завершен

        img = Image.new('RGB', (MATRIX_WIDTH, MATRIX_HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        if self.elapsed < self.spread_duration:
            # Фаза разлета
            progress = self.elapsed / self.spread_duration

            for i, p in enumerate(self.particles):
                particle_start = i / self.num_particles

                if progress > particle_start:
                    local_progress = (progress - particle_start) / (1.0 - particle_start)
                    local_progress = min(1.0, local_progress)

                    if local_progress < 0.1:
                        angle = random.uniform(0, 2 * math.pi)
                        force = self.spread_force * (0.1 - local_progress) * 10
                        p.apply_force(math.cos(angle) * force, math.sin(angle) * force)

                p.update(self.damping)
        else:
            # Фаза сборки
            gather_time = self.elapsed - self.spread_duration
            progress = gather_time / self.gather_duration

            for i, p in enumerate(self.particles):
                target_x = i
                target_y = MATRIX_HEIGHT // 2

                particle_gather = progress * self.num_particles

                if i < particle_gather:
                    dx = target_x - p.x
                    dy = target_y - p.y
                    strength = self.gather_force * (1.0 + (particle_gather - i) * 0.1)
                    p.apply_force(dx * strength * 0.1, dy * strength * 0.1)
                else:
                    dx = target_x - p.x
                    dy = target_y - p.y
                    p.apply_force(dx * 0.01, dy * 0.01)

                p.update(self.damping)

        # Рисуем частицы
        for p in self.particles:
            x = int(round(p.x))
            y = int(round(p.y))
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                draw.point((x, y), fill=(255, 255, 255))

        return img

# ============================================
# ЭФФЕКТ 7: ОДНА СИНУСОИДА
# ============================================
class OneSineEffect:
    def __init__(self):
        self.name = "Одна синусоида"
        self.elapsed = 0
        self.frame_count = 0

        # Рандомизация
        self.static_duration = random.uniform(2, 4)
        self.increase_duration = random.uniform(18, 22)
        self.decrease_duration = random.uniform(18, 22)
        self.max_amplitude = random.randint(20, 30)
        self.max_frequency = random.uniform(3, 5)
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    def ease_in_out(self, t):
        return t * t * (3.0 - 2.0 * t)

    def generate_frame(self):
        self.elapsed += 1.0 / 60

        total_duration = self.static_duration + self.increase_duration + self.decrease_duration
        if self.elapsed >= total_duration:
            return None  # Эффект завершен

        if self.elapsed < self.static_duration:
            amplitude = 0
            frequency = 0
            phase_offset = 0
        elif self.elapsed < self.static_duration + self.increase_duration:
            t = (self.elapsed - self.static_duration) / self.increase_duration
            t_smooth = self.ease_in_out(t)
            amplitude = self.max_amplitude * t_smooth
            frequency = self.max_frequency * t_smooth
            phase_offset = self.frame_count * 0.1
        else:
            t = (self.elapsed - self.static_duration - self.increase_duration) / self.decrease_duration
            t_smooth = self.ease_in_out(t)
            amplitude = self.max_amplitude * (1 - t_smooth)
            frequency = self.max_frequency * (1 - t_smooth)
            phase_offset = self.frame_count * 0.1

        image = Image.new("RGB", (MATRIX_WIDTH, MATRIX_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        line_y = MATRIX_HEIGHT / 2
        prev_x = 0
        prev_y = line_y

        for x in range(MATRIX_WIDTH):
            y = line_y + int(amplitude * math.sin(frequency * 2 * math.pi * x / MATRIX_WIDTH + phase_offset))
            y = max(0, min(MATRIX_HEIGHT - 1, y))

            if x > 0:
                draw.line([(prev_x, prev_y), (x, y)], fill=self.color, width=1)
            else:
                draw.point((x, int(y)), fill=self.color)

            prev_x = x
            prev_y = y

        self.frame_count += 1
        return image

# ============================================
# МЕНЕДЖЕР ЭФФЕКТОВ
# ============================================
class EffectManager:
    def __init__(self):
        self.effects = [

            RGBLinesEffect,
            RotatingLineEffect,
            ChangingSquareEffect,
            ThreeSinesEffect,
            GravityEffect,
            OneSineEffect
        ]
        self.current_effect = None
        self.effect_queue = []
        self.create_random_queue()

    def create_random_queue(self):
        """Создает случайную очередь эффектов"""
        self.effect_queue = random.sample(self.effects, len(self.effects))
        print("\n=== Новая очередь эффектов ===")
        for i, effect_class in enumerate(self.effect_queue, 1):
            temp_effect = effect_class()
            print(f"{i}. {temp_effect.name}")
        print("=" * 30 + "\n")

    def get_next_effect(self):
        """Получает следующий эффект из очереди"""
        if not self.effect_queue:
            self.create_random_queue()

        effect_class = self.effect_queue.pop(0)
        self.current_effect = effect_class()
        print(f"\n>>> Запуск эффекта: {self.current_effect.name}")
        return self.current_effect

    def run(self):
        """Главный цикл запуска эффектов"""
        try:
            print("=" * 50)
            print("МЕНЕДЖЕР ЭФФЕКТОВ LED-МАТРИЦЫ")
            print("=" * 50)
            print("Нажмите CTRL-C для остановки\n")

            fps = 60
            frame_delay = 1.0 / fps

            while True:
                effect = self.get_next_effect()

                while True:
                    frame = effect.generate_frame()

                    if frame is None:
                        print(f"<<< Эффект '{effect.name}' завершен\n")
                        break

                    matrix.SetImage(frame.convert("RGB"))
                    time.sleep(frame_delay)

        except KeyboardInterrupt:
            print("\n\nОстановка программы...")
            matrix.Clear()
            print("Завершено.")

# ============================================
# ЗАПУСК
# ============================================
if __name__ == "__main__":
    manager = EffectManager()
    manager.run()
