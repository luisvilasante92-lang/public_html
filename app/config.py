"""
Конфигурация приложения
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
# Корень проекта (родитель папки app)
project_root = os.path.abspath(os.path.join(basedir, '..'))


def _resolve_sqlite_uri(uri):
    """
    Преобразует относительный путь SQLite в абсолютный.
    На shared-хостинге относительные пути могут не работать из-за CWD.
    """
    if not uri or not uri.startswith('sqlite:///'):
        return uri
    path_part = uri.replace('sqlite:///', '')
    if not path_part or path_part == ':memory:':
        return uri
    if os.path.isabs(path_part):
        return uri
    # Относительный путь — делаем абсолютным относительно project_root
    abs_path = os.path.normpath(os.path.join(project_root, path_part))
    return 'sqlite:///' + abs_path.replace('\\', '/')

# Поддерживаемые БД (для справки):
# - SQLite 3 — разработка и тесты (встроен в Python).
# - MySQL 5.7+ / MariaDB 10.3+ — mysql+pymysql://user:pass@host:3306/dbname
# - PostgreSQL 12+ — postgresql://user:pass@host:5432/dbname
# SQLAlchemy 2.x совместим со всеми.
DB_ENGINE_DEV = 'sqlite'
DB_ENGINE_PROD = 'mysql'
DB_VERSION_RECOMMENDED = 'SQLite 3.x / MySQL 5.7+ / PostgreSQL 12+'


class Config:
    """Базовая конфигурация"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Загрузка файлов
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB максимум
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'uploads')
    
    # Лимиты размеров файлов
    MAX_COVER_SIZE = int(os.environ.get('MAX_COVER_SIZE', 10 * 1024 * 1024))
    MAX_TRACK_SIZE = int(os.environ.get('MAX_TRACK_SIZE', 100 * 1024 * 1024))
    MAX_AVATAR_SIZE = int(os.environ.get('MAX_AVATAR_SIZE', 5 * 1024 * 1024))
    MAX_NEWS_COVER_SIZE = int(os.environ.get('MAX_NEWS_COVER_SIZE', 5 * 1024 * 1024))
    MAX_FINANCE_FILE_SIZE = int(os.environ.get('MAX_FINANCE_FILE_SIZE', 10 * 1024 * 1024))
    MAX_CONTRACT_SIZE = int(os.environ.get('MAX_CONTRACT_SIZE', 10 * 1024 * 1024))
    
    # Разрешённые расширения
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    ALLOWED_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    ALLOWED_NEWS_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    ALLOWED_TRACK_EXTENSIONS = {'wav'}
    ALLOWED_FINANCE_EXTENSIONS = {'csv'}
    ALLOWED_CONTRACT_EXTENSIONS = {'pdf'}
    
    # Внешние сервисы (основной домен: luisv-records.ru; поддомены: auth. — вход, lk. — ЛК, lnk., s3.)
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'https://auth.luisv-records.ru')
    AUTH_CALLBACK_URL = os.environ.get('AUTH_CALLBACK_URL', 'https://lk.luisv-records.ru/auth/callback')
    SMART_LINK_BASE_URL = os.environ.get('SMART_LINK_BASE_URL', 'https://lk.luisv-records.ru/link')
    
    # Основной домен сайта (вход: https://auth.luisv-records.ru, после входа: https://lk.luisv-records.ru).
    APPLICATION_ROOT_URL = os.environ.get('APPLICATION_ROOT_URL', 'https://luisv-records.ru')
    
    # S3 хранилище (опционально)
    S3_URL = os.environ.get('S3_URL')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    
    # Пагинация
    RELEASES_PER_PAGE = 12

    # Жанры для релизов (выбор из списка)
    RELEASE_GENRES = [
        'Pop', 'Hip-Hop', 'Rap', 'Rock', 'Alternative', 'Indie', 'Electronic',
        'Dance', 'House', 'Techno', 'Trance', 'R&B', 'Soul', 'Jazz', 'Blues',
        'Country', 'Folk', 'Classical', 'Metal', 'Punk', 'Reggae', 'Latin',
        'World', 'Ambient', 'Soundtrack', 'Children', 'Religion', 'Comedy',
        'Spoken Word', 'Другое'
    ]
    USERS_PER_PAGE = 20
    NEWS_PER_PAGE = 10
    TICKETS_PER_PAGE = 15

    # Email (Flask-Mail). Beget: порт 2525 (STARTTLS) или 465 (SSL), порт 587 не поддерживается
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 2525))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'  # для порта 465
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@luisv-records.ru')

    # Email для уведомлений о тикетах (исполнителям). Если задан — письма идут туда, иначе — всем админам
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL')

    # ЮKassa (доп. услуги: видео/рингтоны)
    YOOKASSA_SHOP_ID = os.environ.get('YOOKASSA_SHOP_ID', '1241273')

    # SMS Aero (коды авторизации по SMS)
    SMSAERO_EMAIL = os.environ.get('SMSAERO_EMAIL')
    SMSAERO_API_KEY = os.environ.get('SMSAERO_API_KEY')
    SMSAERO_SIGN = os.environ.get('SMSAERO_SIGN', 'общее')
    # При ошибке SSL CERTIFICATE_VERIFY_FAILED на shared-хостинге: SMSAERO_SSL_VERIFY=false
    SMSAERO_SSL_VERIFY = os.environ.get('SMSAERO_SSL_VERIFY', 'true').lower() not in ('0', 'false', 'no')


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    
    DEBUG = True
    _default_sqlite = 'sqlite:///' + os.path.join(project_root, 'instance', 'lksystem.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = _resolve_sqlite_uri(
        os.environ.get('DATABASE_URL') or _default_sqlite
    )
    
    # Отключаем безопасные куки для разработки
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _resolve_sqlite_uri(os.environ.get('DATABASE_URL'))
    
    # Дополнительная безопасность
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
