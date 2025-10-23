# НАЗВАНИЕ: алгоритм поиска BFS
# ОПИСАНИЕ: Гарантия - всегда находит кратчайший путь
import time
import random
import platform

if platform.system() == "Windows":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    graphics = None  # если нужно
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw
from collections import deque

# Конфигурация для матрицы
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Цвета
COLOR_WALL = (48, 72, 97)      # стены - серые
COLOR_PATH = (0, 0, 0)            # Черный - дорожки
COLOR_START = (18, 121, 227)         # Синий - начало
COLOR_END = (224, 16, 1)           # Красный - конец
COLOR_SEARCH = (139, 53, 46)      # темно красный - поиск
COLOR_FINAL = (199, 224, 0)       # лайм - финальный путь

class Maze:
    def __init__(self, width=64, height=64, cell_size=1):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_w = width // cell_size
        self.grid_h = height // cell_size
        self.maze = [[1 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        # Старт в углу
        self.start = (2, 2)
        # Финиш в случайной позиции внутри лабиринта
        self.end = self._random_inner_position()

    def _random_inner_position(self):
        """Генерирует случайную позицию внутри лабиринта (не на краях)"""
        # Выбираем позицию в центральной области
        min_dist = self.grid_h // 4
        max_dist = 3 * self.grid_h // 4

        y = random.randint(min_dist, max_dist)
        x = random.randint(min_dist, max_dist)

        # Убеждаемся что координаты четные
        if y % 2 == 1:
            y -= 1
        if x % 2 == 1:
            x -= 1

        return (y, x)

    def generate(self):
        """Генерация сложного извилистого лабиринта"""
        self.maze = [[1 for _ in range(self.grid_w)] for _ in range(self.grid_h)]

        # Начинаем генерацию со старта
        visited = set()
        stack = [self.start]

        while stack:
            y, x = stack[-1]
            self.maze[y][x] = 0
            visited.add((y, x))

            # Получаем всех соседей на расстоянии 2
            neighbors = []
            for dy, dx in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                ny, nx = y + dy, x + dx
                if (2 <= ny < self.grid_h - 2 and 2 <= nx < self.grid_w - 2 and
                    (ny, nx) not in visited):
                    neighbors.append((ny, nx, dy, dx))

            if neighbors:
                # Выбираем случайного соседа
                ny, nx, dy, dx = random.choice(neighbors)
                # Пробиваем стену между текущей клеткой и соседом
                self.maze[y + dy//2][x + dx//2] = 0
                stack.append((ny, nx))
            else:
                stack.pop()

        # Добавляем дополнительные проходы для усложнения
        self._add_extra_passages()

        # Гарантируем проходимость старта и финиша
        self.maze[self.start[0]][self.start[1]] = 0
        self.maze[self.end[0]][self.end[1]] = 0

        # Убеждаемся что финиш достижим
        if not self._is_reachable():
            self._create_path_to_end()

    def _add_extra_passages(self):
        """Добавляет дополнительные проходы для создания альтернативных путей"""
        walls_to_remove = []

        # Находим стены, которые можно убрать
        for y in range(2, self.grid_h - 2):
            for x in range(2, self.grid_w - 2):
                if self.maze[y][x] == 1:  # Это стена
                    # Проверяем, есть ли проходы с двух сторон
                    if (self.maze[y-1][x] == 0 and self.maze[y+1][x] == 0) or \
                       (self.maze[y][x-1] == 0 and self.maze[y][x+1] == 0):
                        walls_to_remove.append((y, x))

        # Убираем случайные 15% от найденных стен
        num_to_remove = max(1, len(walls_to_remove) // 7)
        for y, x in random.sample(walls_to_remove, min(num_to_remove, len(walls_to_remove))):
            self.maze[y][x] = 0

    def get_neighbors(self, pos):
        """Получить соседние клетки"""
        y, x = pos
        neighbors = []
        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.grid_h and 0 <= nx < self.grid_w and self.maze[ny][nx] == 0:
                neighbors.append((ny, nx))
        return neighbors

    def _is_reachable(self):
        """Проверяет, достижим ли финиш от старта"""
        visited = {self.start}
        queue = deque([self.start])

        while queue:
            current = queue.popleft()
            if current == self.end:
                return True

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    def _create_path_to_end(self):
        """Создает прямой путь от старта к финишу если он недостижим"""
        sy, sx = self.start
        ey, ex = self.end

        # Простой путь по горизонтали и вертикали
        y, x = sy, sx

        # Идем к финишу по вертикали
        while y != ey:
            self.maze[y][x] = 0
            y += 1 if y < ey else -1
            self.maze[y][x] = 0

        # Идем к финишу по горизонтали
        while x != ex:
            self.maze[y][x] = 0
            x += 1 if x < ex else -1
            self.maze[y][x] = 0

    def bfs_search(self):
        """Поиск в ширину с сохранением истории"""
        queue = deque([(self.start, [self.start])])
        visited = {self.start}
        search_order = []
        final_path = []

        while queue:
            current, path = queue.popleft()
            search_order.append(current)

            if current == self.end:
                final_path = path
                break

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return search_order, final_path

def draw_maze_frame(maze, search_progress=None, final_path=None):
    """Рисует текущее состояние лабиринта"""
    img = Image.new('RGB', (maze.width, maze.height), COLOR_PATH)
    draw = ImageDraw.Draw(img)

    # Рисуем лабиринт
    for y in range(maze.grid_h):
        for x in range(maze.grid_w):
            px = x * maze.cell_size
            py = y * maze.cell_size

            if maze.maze[y][x] == 1:
                # Стена
                draw.rectangle([px, py, px + maze.cell_size - 1, py + maze.cell_size - 1],
                              fill=COLOR_WALL)
            else:
                # Дорожка
                draw.rectangle([px, py, px + maze.cell_size - 1, py + maze.cell_size - 1],
                              fill=COLOR_PATH)

    # Рисуем поиск (фиолетовым)
    if search_progress:
        for y, x in search_progress:
            if (y, x) != maze.start and (y, x) != maze.end:
                px = x * maze.cell_size
                py = y * maze.cell_size
                draw.rectangle([px, py, px + maze.cell_size - 1, py + maze.cell_size - 1],
                              fill=COLOR_SEARCH)

    # Рисуем финальный путь (голубым)
    if final_path:
        for y, x in final_path:
            if (y, x) != maze.start and (y, x) != maze.end:
                px = x * maze.cell_size
                py = y * maze.cell_size
                draw.rectangle([px, py, px + maze.cell_size - 1, py + maze.cell_size - 1],
                              fill=COLOR_FINAL)

    # Рисуем старт (синим)
    sy, sx = maze.start
    draw.rectangle([sx * maze.cell_size, sy * maze.cell_size,
                   sx * maze.cell_size + maze.cell_size - 1,
                   sy * maze.cell_size + maze.cell_size - 1],
                  fill=COLOR_START)

    # Рисуем финиш (красным)
    ey, ex = maze.end
    draw.rectangle([ex * maze.cell_size, ey * maze.cell_size,
                   ex * maze.cell_size + maze.cell_size - 1,
                   ey * maze.cell_size + maze.cell_size - 1],
                  fill=COLOR_END)

    return img

# Анимация
try:
    print("Press CTRL-C to stop.")
    print("Визуализация поиска пути в лабиринте...")

    # iteration = 0
    while True:
        # iteration += 1
        # print(f"\n=== Итерация {iteration} ===")

        # Генерируем новый лабиринт
        # print("Генерация лабиринта...")
        maze = Maze(width=64, height=64, cell_size=1)
        maze.generate()
        # print(f"Лабиринт сгенерирован! Финиш в позиции {maze.end}")

        # Выполняем поиск
        # print("Выполняется поиск пути...")
        search_order, final_path = maze.bfs_search()

        # print(f"✓ Путь найден: {len(final_path)} клеток")
        # print(f"  Исследовано: {len(search_order)} клеток")

        # Фаза 1: Показываем поиск всех путей (фиолетовым)
        # print("Фаза 1: Анимация поиска...")
        for i in range(0, len(search_order), 10):
            frame = draw_maze_frame(maze, search_progress=search_order[:i+10])
            matrix.SetImage(frame.convert("RGB"))
            time.sleep(0.005)

        # Показываем весь поиск на секунду
        frame = draw_maze_frame(maze, search_progress=search_order)
        matrix.SetImage(frame.convert("RGB"))
        time.sleep(0.5)

        # Фаза 2: Показываем только финальный путь (голубым)
        # print("Фаза 2: Отображение финального пути...")
        frame = draw_maze_frame(maze, search_progress=None, final_path=final_path)
        matrix.SetImage(frame.convert("RGB"))

        # Фаза 3: Таймаут 3 секунды с отображением пути
        # print("Фаза 3: Пауза 3 секунды...")
        time.sleep(3)

        # print("Переход к новому лабиринту...")

except KeyboardInterrupt:
    print("\n\nExiting...")
    matrix.Clear()