"""
Утилиты для работы с файлами
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename, allowed_extensions):
    """Проверка разрешённого расширения файла"""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(file, subfolder):
    """
    Сохранение загруженного файла
    
    Args:
        file: FileStorage объект
        subfolder: подпапка в uploads (например, 'covers', 'tracks')
    
    Returns:
        Имя сохранённого файла или None при ошибке
    """
    if not file or not file.filename:
        return None
    
    # Генерация уникального имени файла
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f'{uuid.uuid4().hex}.{ext}' if ext else uuid.uuid4().hex
    
    # Путь для сохранения
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    
    try:
        file.save(file_path)
        return unique_filename
    except Exception as e:
        current_app.logger.error(f'Ошибка сохранения файла: {e}')
        return None


def delete_file(filename, subfolder):
    """
    Удаление файла
    
    Args:
        filename: имя файла
        subfolder: подпапка в uploads
    
    Returns:
        True при успешном удалении, False при ошибке
    """
    if not filename:
        return False
    
    file_path = os.path.join(current_app.root_path, '..', 'uploads', subfolder, filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f'Ошибка удаления файла: {e}')
        return False


def get_file_size(filename, subfolder):
    """Получение размера файла в байтах"""
    if not filename:
        return 0
    
    file_path = os.path.join(current_app.root_path, '..', 'uploads', subfolder, filename)
    
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception:
        return 0


def format_file_size(size_bytes):
    """Форматирование размера файла"""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.1f} GB'
