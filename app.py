#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask веб-сервер для управления LED эффектами
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import subprocess
import signal
import sys
from pathlib import Path
import yaml

app = Flask(__name__)

# Глобальная переменная для хранения процесса текущего эффекта
current_effect_process = None
current_effect_name = None

EFFECTS_DIR = Path(__file__).parent / "effects"
CONFIG_FILE = Path(__file__).parent / "config.yaml"
IMAGES_DIR = Path(__file__).parent / "templates" / "images"


def load_config():
    """
    Загружает конфигурацию эффектов из config.yaml
    """
    if not CONFIG_FILE.exists():
        print(f"Предупреждение: Файл конфигурации {CONFIG_FILE} не найден")
        return []

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('effects', [])
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
        return []


def get_effect_metadata(effect_file):
    """
    Извлекает метаданные (название и описание) из файла эффекта.
    Метаданные должны быть в виде комментариев в начале файла:
    # НАЗВАНИЕ: Название эффекта
    # ОПИСАНИЕ: Описание эффекта
    """
    metadata = {
        'filename': effect_file.stem,
        'name': None,
        'description': None
    }

    try:
        with open(effect_file, 'r', encoding='utf-8') as f:
            lines_read = 0
            for line in f:
                line = line.strip()
                if line.startswith('# НАЗВАНИЕ:'):
                    metadata['name'] = line.replace('# НАЗВАНИЕ:', '').strip()
                elif line.startswith('# ОПИСАНИЕ:'):
                    metadata['description'] = line.replace('# ОПИСАНИЕ:', '').strip()
                # Останавливаемся после первых 20 строк
                lines_read += 1
                if lines_read > 20:
                    break
    except Exception as e:
        print(f"Ошибка при чтении метаданных из {effect_file}: {e}")

    return metadata


def get_available_effects():
    """
    Загружает список доступных эффектов из config.yaml.
    Возвращает только те эффекты, файлы которых существуют.
    """
    effects = []
    config_effects = load_config()

    for effect in config_effects:
        effect_file = EFFECTS_DIR / f"{effect['file']}.py"

        # Проверяем, что файл эффекта существует
        if effect_file.exists():
            effects.append({
                'filename': effect['file'],
                'name': effect['name'],
                'description': effect.get('description', ''),
                'image': effect.get('image', '')
            })
        else:
            print(f"Предупреждение: Файл эффекта {effect_file} не найден")

    return effects


@app.route('/')
def index():
    """Главная страница с интерфейсом управления"""
    return render_template('index.html')


@app.route('/images/<path:filename>')
def serve_image(filename):
    """Обслуживание изображений эффектов"""
    return send_from_directory(IMAGES_DIR, filename)


@app.route('/api/effects', methods=['GET'])
def list_effects():
    """API: получить список всех доступных эффектов"""
    effects = get_available_effects()
    return jsonify(effects)


@app.route('/api/effects/current', methods=['GET'])
def get_current_effect():
    """API: получить название текущего запущенного эффекта"""
    return jsonify({
        'running': current_effect_name is not None,
        'effect': current_effect_name
    })


@app.route('/api/effects/start', methods=['POST'])
def start_effect():
    """API: запустить эффект"""
    global current_effect_process, current_effect_name

    data = request.get_json()
    effect_name = data.get('effect')

    if not effect_name:
        return jsonify({'success': False, 'error': 'Не указано название эффекта'}), 400

    effect_file = EFFECTS_DIR / f"{effect_name}.py"

    if not effect_file.exists():
        return jsonify({'success': False, 'error': 'Эффект не найден'}), 404

    # Остановить текущий эффект, если он запущен
    if current_effect_process:
        try:
            current_effect_process.terminate()
            current_effect_process.wait(timeout=3)
        except:
            current_effect_process.kill()
        current_effect_process = None
        current_effect_name = None

    # Запустить новый эффект
    try:
        current_effect_process = subprocess.Popen(
            [sys.executable, str(effect_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(EFFECTS_DIR)
        )
        current_effect_name = effect_name

        return jsonify({
            'success': True,
            'effect': effect_name,
            'message': f'Эффект "{effect_name}" запущен'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при запуске эффекта: {str(e)}'
        }), 500


@app.route('/api/effects/stop', methods=['POST'])
def stop_effect():
    """API: остановить текущий эффект"""
    global current_effect_process, current_effect_name

    if not current_effect_process:
        return jsonify({'success': False, 'error': 'Нет запущенного эффекта'}), 400

    try:
        current_effect_process.terminate()
        current_effect_process.wait(timeout=3)
    except:
        current_effect_process.kill()

    stopped_effect = current_effect_name
    current_effect_process = None
    current_effect_name = None

    return jsonify({
        'success': True,
        'message': f'Эффект "{stopped_effect}" остановлен'
    })


def signal_handler(_sig, _frame):
    """Обработчик сигнала для корректного завершения"""
    global current_effect_process

    print('\nОстановка сервера...')

    if current_effect_process:
        try:
            current_effect_process.terminate()
            current_effect_process.wait(timeout=3)
        except:
            current_effect_process.kill()

    sys.exit(0)


if __name__ == '__main__':
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 50)
    print("LED Effects Control Server")
    print("=" * 50)
    print(f"Папка с эффектами: {EFFECTS_DIR}")
    print(f"Доступно эффектов: {len(get_available_effects())}")
    print("=" * 50)

    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=5000, debug=True)
