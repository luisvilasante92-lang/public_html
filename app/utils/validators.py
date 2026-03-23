"""
Валидаторы
"""

import re


def validate_password(password):
    """
    Валидация пароля
    
    Требования:
    - Минимум 8 символов
    - Минимум одна заглавная буква
    - Минимум одна строчная буква
    - Минимум одна цифра
    - Минимум один спецсимвол
    
    Returns:
        Список ошибок (пустой список, если пароль валиден)
    """
    errors = []
    
    if len(password) < 8:
        errors.append('Пароль должен содержать минимум 8 символов')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Пароль должен содержать минимум одну заглавную букву')
    
    if not re.search(r'[a-z]', password):
        errors.append('Пароль должен содержать минимум одну строчную букву')
    
    if not re.search(r'\d', password):
        errors.append('Пароль должен содержать минимум одну цифру')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Пароль должен содержать минимум один спецсимвол (!@#$%^&*(),.?":{}|<>)')
    
    return errors


def validate_email(email):
    """
    Валидация email
    
    Returns:
        True если email валиден, False иначе
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_upc(upc):
    """
    Валидация UPC кода
    
    Returns:
        True если UPC валиден, False иначе
    """
    if not upc:
        return True  # UPC опционален
    
    # UPC должен содержать только цифры и быть длиной 12-14 символов
    if not upc.isdigit():
        return False
    
    if len(upc) < 12 or len(upc) > 14:
        return False
    
    return True


def validate_isrc(isrc):
    """
    Валидация ISRC кода
    
    Формат: CC-XXX-YY-NNNNN
    - CC: код страны (2 буквы)
    - XXX: код регистранта (3 символа)
    - YY: год (2 цифры)
    - NNNNN: номер записи (5 цифр)
    
    Returns:
        True если ISRC валиден, False иначе
    """
    if not isrc:
        return True  # ISRC опционален
    
    # Убираем дефисы
    isrc_clean = isrc.replace('-', '').upper()
    
    if len(isrc_clean) != 12:
        return False
    
    # Первые 2 символа - буквы (код страны)
    if not isrc_clean[:2].isalpha():
        return False
    
    # Следующие 3 символа - буквы или цифры
    if not isrc_clean[2:5].isalnum():
        return False
    
    # Остальные 7 символов - цифры
    if not isrc_clean[5:].isdigit():
        return False
    
    return True


def sanitize_filename(filename):
    """
    Очистка имени файла от опасных символов
    """
    # Удаляем путь
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Оставляем только безопасные символы
    safe_chars = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Заменяем пробелы на подчёркивания
    safe_chars = safe_chars.replace(' ', '_')
    
    return safe_chars


def validate_date_format(date_str, format='%Y-%m-%d'):
    """
    Валидация формата даты
    
    Returns:
        True если формат валиден, False иначе
    """
    from datetime import datetime
    
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False
