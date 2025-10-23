#!/usr/bin/env python
# НАЗВАНИЕ: Калейдоскоп
# ОПИСАНИЕ: Психоделический калейдоскопический эффект с плавными цветовыми переходами
import time
import numpy as np
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

# Конфигурация
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
# options.hardware_mapping = 'regular'
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

WIDTH, HEIGHT = 64, 64
start_time = time.time()

# Палитра
def palette(t):
    a = np.array([0.5, 0.5, 0.5])
    b = np.array([0.5, 0.5, 0.5])
    c = np.array([1.0, 1.0, 1.0])
    d = np.array([0.263, 0.416, 0.557])

    t = t[..., np.newaxis]  # расширяем t до (H, W, 1)
    return np.sin(a) + np.cos(b) * np.cos(6.28318 * (c * np.cos(t) + np.sin(d)))
# Предрасчёт сетки координат
x = np.linspace(-1, 1, WIDTH)
y = np.linspace(-1, 1, HEIGHT)
uv_x, uv_y = np.meshgrid(x * WIDTH / HEIGHT, y)
uv0_x, uv0_y = uv_x.copy(), uv_y.copy()
uv0_len = np.sqrt(uv0_x**2 + uv0_y**2)

def generate_frame(current_time):
    uv_x, uv_y = uv0_x.copy(), uv0_y.copy()
    final_color = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)

    for i in range(4):
        uv_x = (uv_x * 1.5) % 1.0 - 0.5
        uv_y = (uv_y * 1.5) % 1.0 - 0.5

        d = np.sqrt(uv_x**2 + uv_y**2)
        d *= np.exp(-uv0_len)
        col = palette(uv0_len + i * 0.4 + current_time * 0.4)

        d = np.sin(d * 8.0 + current_time) / 8.0
        d = np.abs(d) / 0.4
        d = np.where(d > 0.001, np.power(0.01 / d, 1.2), 0)

        final_color += col * d[..., np.newaxis]

    final_color = np.clip(final_color * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(final_color, 'RGB')

# Основной цикл
try:
    print("Запуск анимации на LED панели 64x64... (CTRL-C для остановки)")
    while True:
        frame = generate_frame(time.time() - start_time)
        matrix.SetImage(frame)
        time.sleep(0.03)
except KeyboardInterrupt:
    print("\nОстановка анимации...")
    matrix.Clear()
    print("Завершено.")
