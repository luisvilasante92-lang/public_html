"""
Личный кабинет luisv-records.ru
Фабрика Flask-приложения
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Фабрика приложения"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Загрузка конфигурации
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import config
    if config_name not in config:
        config_name = 'development'
    app.config.from_object(config[config_name])
    if config_name == 'production' and not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise ValueError('DATABASE_URL обязателен для production')
    
    # В production за прокси: доверяем X-Forwarded-Host/Proto, чтобы url_for(..., _external=True) давал основной домен (luisv-records.ru)
    if config_name == 'production':
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Создание директории instance
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Для SQLite: гарантированно создаём папку с БД (на shared-хостинге часто отсутствует)
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        path_part = db_uri.replace('sqlite:///', '')
        if path_part and path_part != ':memory:':
            db_dir = os.path.dirname(path_part)
            if db_dir:
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except OSError as e:
                    raise RuntimeError(
                        f'Не удалось создать папку для БД: {db_dir}. '
                        f'Проверьте права доступа. Ошибка: {e}'
                    ) from e
    
    # Создание директорий для загрузок
    upload_dirs = [
        'uploads/covers',
        'uploads/tracks',
        'uploads/avatars',
        'uploads/news_covers',
        'uploads/finances',
        'uploads/contracts/original',
        'uploads/contracts/signed'
    ]
    for directory in upload_dirs:
        dir_path = os.path.join(app.root_path, '..', directory)
        os.makedirs(dir_path, exist_ok=True)
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.utils.email import init_mail
    init_mail(app)
    
    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему'
    login_manager.login_message_category = 'warning'
    
    # Загрузчик пользователя
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None:
            return None
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None
    
    # Регистрация blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.releases import releases_bp
    from app.routes.moderation import moderation_bp
    from app.routes.money import money_bp
    from app.routes.smart_link import smart_link_bp
    from app.routes.stories import stories_bp
    from app.routes.tickets import tickets_bp
    from app.routes.knowledge import knowledge_bp
    from app.routes.tools import tools_bp
    from app.routes.notifications import notifications_bp
    from app.routes.contracts import contracts_bp
    from app.routes.users import users_bp
    from app.routes.labels import labels_bp
    from app.routes.profile import profile_bp
    from app.routes.admin import admin_bp
    from app.routes.stats import stats_bp
    from app.routes.ringtones_video import ringtones_video_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(releases_bp)
    app.register_blueprint(moderation_bp)
    app.register_blueprint(money_bp)
    app.register_blueprint(smart_link_bp)
    app.register_blueprint(stories_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(labels_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(ringtones_video_bp)

    # Обработчики ошибок
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # Контекстный процессор для шаблонов
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from flask_login import current_user
        data = {
            'current_year': datetime.now().year,
            'current_quarter': (datetime.now().month - 1) // 3 + 1
        }
        if current_user.is_authenticated:
            data['unread_notifications_count'] = 0
            try:
                from app.models.notification import Notification
                data['unread_notifications_count'] = Notification.query.filter_by(
                    user_id=current_user.id, is_read=False
                ).count()
            except Exception:
                pass
        else:
            data['unread_notifications_count'] = 0
        # Всегда задаём has_endpoint до любых других обращений к БД в шаблонах
        def _has_endpoint(name):
            try:
                return name in app.view_functions
            except Exception:
                return False
        data['has_endpoint'] = _has_endpoint
        return data
    
    # Создание таблиц БД
    with app.app_context():
        from app.models.knowledge_article import KnowledgeArticle  # noqa: F401
        from app.models.knowledge_section import KnowledgeSection  # noqa: F401
        from app.models.knowledge_topic import KnowledgeTopic  # noqa: F401
        from app.models.finance import FinancePlatformLine  # noqa: F401
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning('db.create_all(): %s', e)
        try:
            from app.utils.knowledge_migrate import run_knowledge_migrations
            run_knowledge_migrations(app)
        except Exception as e:
            app.logger.warning('run_knowledge_migrations: %s', e)
        _ensure_knowledge_article_topic_id_column(app)
        _ensure_contract_rejection_reason_column(app)
        _ensure_auto_form_columns(app)
        _ensure_video_request_columns(app)
        _ensure_user_phone_column(app)
        _ensure_user_tax_profile_columns(app)

    return app


def _ensure_knowledge_article_topic_id_column(app):
    """Таблица knowledge_topics + колонка topic_id у статей (подразделы / вкладки)."""
    try:
        from sqlalchemy import inspect, text

        insp = inspect(db.engine)
        tables = insp.get_table_names()
        if 'knowledge_articles' not in tables:
            return
        cols = {c['name'] for c in insp.get_columns('knowledge_articles')}
        if 'topic_id' in cols:
            return
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    'ALTER TABLE knowledge_articles ADD COLUMN topic_id INTEGER NULL'
                )
            )
    except Exception as e:
        msg = str(e).lower()
        if 'duplicate column' in msg or 'already exists' in msg or 'topic_id' in msg:
            pass
        else:
            app.logger.warning('Миграция knowledge_articles.topic_id: %s', e)


def _ensure_contract_rejection_reason_column(app):
    """Добавить колонку rejection_reason в contracts, если её ещё нет (миграция без Flask-Migrate)."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE contracts ADD COLUMN rejection_reason TEXT"))
            conn.commit()
    except Exception as e:
        msg = str(e).lower()
        if 'duplicate column' in msg or 'already exists' in msg or 'rejection_reason' in msg:
            pass
        else:
            app.logger.warning('Миграция contracts.rejection_reason: %s', e)


def _ensure_auto_form_columns(app):
    """Добавить колонку artist_name в auto_form_requests, если её ещё нет."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE auto_form_requests ADD COLUMN artist_name VARCHAR(256)"))
            conn.commit()
    except Exception as e:
        msg = str(e).lower()
        if 'duplicate column' in msg or 'already exists' in msg or 'artist_name' in msg:
            pass
        else:
            app.logger.warning('Миграция auto_form_requests.artist_name: %s', e)


def _ensure_user_tax_profile_columns(app):
    """Колонки налоговой и платёжной информации в users."""
    from sqlalchemy import text

    statements = [
        "ALTER TABLE users ADD COLUMN tax_status VARCHAR(32)",
        "ALTER TABLE users ADD COLUMN tax_legal_name VARCHAR(512)",
        "ALTER TABLE users ADD COLUMN tax_inn VARCHAR(12)",
        "ALTER TABLE users ADD COLUMN tax_bank_account VARCHAR(32)",
        "ALTER TABLE users ADD COLUMN tax_bank_name VARCHAR(256)",
        "ALTER TABLE users ADD COLUMN tax_bank_bik VARCHAR(9)",
    ]
    for sql in statements:
        try:
            with db.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
        except Exception as e:
            msg = str(e).lower()
            if 'duplicate column' in msg or 'already exists' in msg:
                pass
            else:
                app.logger.warning('Миграция users tax: %s — %s', sql[:50], e)


def _ensure_user_phone_column(app):
    """Добавить колонку phone в users, если её ещё нет (для SMS-кодов авторизации)."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
            conn.commit()
    except Exception as e:
        msg = str(e).lower()
        if 'duplicate column' in msg or 'already exists' in msg or 'phone' in msg:
            pass
        else:
            app.logger.warning('Миграция users.phone: %s', e)


def _ensure_video_request_columns(app):
    """Добавить колонки service_type и lyrics_text в video_requests, если их ещё нет."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE video_requests ADD COLUMN service_type VARCHAR(20) DEFAULT 'video'"))
            conn.commit()
    except Exception as e:
        msg = str(e).lower()
        if 'duplicate column' in msg or 'already exists' in msg or 'service_type' in msg:
            pass
        else:
            app.logger.warning('Миграция video_requests.service_type: %s', e)
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE video_requests ADD COLUMN lyrics_text TEXT"))
            conn.commit()
    except Exception as e:
        msg = str(e).lower()
        if 'duplicate column' in msg or 'already exists' in msg or 'lyrics_text' in msg:
            pass
        else:
            app.logger.warning('Миграция video_requests.lyrics_text: %s', e)
