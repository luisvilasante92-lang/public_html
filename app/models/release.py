"""
Модели релизов, треков и платформ
"""

from datetime import datetime
from app import db


class Release(db.Model):
    """Музыкальные релизы"""
    
    __tablename__ = 'releases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    cover = db.Column(db.String(256), nullable=True)
    title = db.Column(db.String(256), nullable=False)
    version = db.Column(db.String(100), nullable=True)
    artists = db.Column(db.String(512), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='Single')  # Single, EP, Album
    genre = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    yandex_presave = db.Column(db.Boolean, default=False)
    partner_code = db.Column(db.String(50), nullable=True)
    copyright = db.Column(db.String(256), nullable=True)
    upc = db.Column(db.String(20), nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default='draft', index=True)
    # Статусы: draft, moderation, approved, rejected, deletion
    moderator_comment = db.Column(db.Text, nullable=True)
    platforms = db.Column(db.JSON, nullable=True)  # Список ID платформ
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    tracks = db.relationship('Track', backref='release', lazy='dynamic',
                             cascade='all, delete-orphan')
    analytics = db.relationship('ReleaseAnalytics', backref='release', lazy='dynamic',
                                cascade='all, delete-orphan')
    smart_links = db.relationship('SmartLink', backref='release', lazy='dynamic')
    
    @property
    def cover_url(self):
        """URL обложки"""
        if self.cover:
            return f'/uploads/covers/{self.cover}'
        return '/static/img/default-cover.png'
    
    @property
    def tracks_count(self):
        """Количество треков"""
        return self.tracks.count()
    
    @property
    def status_display(self):
        """Отображаемый статус"""
        statuses = {
            'draft': 'Черновик',
            'moderation': 'На модерации',
            'approved': 'Одобрено',
            'rejected': 'Отклонено',
            'deletion': 'На удалении'
        }
        return statuses.get(self.status, self.status)
    
    @property
    def status_class(self):
        """CSS класс для статуса"""
        classes = {
            'draft': 'status-draft',
            'moderation': 'status-moderation',
            'approved': 'status-approved',
            'rejected': 'status-rejected',
            'deletion': 'status-deletion'
        }
        return classes.get(self.status, '')
    
    @property
    def type_display(self):
        """Отображаемый тип"""
        types = {
            'Single': 'Сингл',
            'EP': 'EP',
            'Album': 'Альбом'
        }
        return types.get(self.type, self.type)
    
    def can_edit(self):
        """Можно ли редактировать релиз"""
        return self.status in ['draft', 'rejected']
    
    def can_submit(self):
        """Можно ли отправить на модерацию"""
        return self.status in ['draft', 'rejected'] and self.cover and self.tracks_count > 0
    
    def can_delete(self):
        """Можно ли запросить удаление"""
        return self.status in ['draft', 'approved', 'rejected']
    
    def __repr__(self):
        return f'<Release {self.title}>'


class Track(db.Model):
    """Треки релизов"""
    
    __tablename__ = 'tracks'
    
    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False, index=True)
    wav_file = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    version = db.Column(db.String(100), nullable=True)
    artists = db.Column(db.String(512), nullable=False)
    composers = db.Column(db.String(512), nullable=True)
    authors = db.Column(db.String(512), nullable=True)
    explicit = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(50), nullable=True)
    isrc = db.Column(db.String(20), nullable=True)
    lyrics = db.Column(db.Text, nullable=True)
    track_order = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @property
    def file_url(self):
        """URL файла трека"""
        return f'/uploads/tracks/{self.wav_file}'
    
    @property
    def display_title(self):
        """Полное название трека с версией"""
        if self.version:
            return f'{self.title} ({self.version})'
        return self.title
    
    def __repr__(self):
        return f'<Track {self.title}>'


class Platform(db.Model):
    """Платформы распространения"""
    
    __tablename__ = 'platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    # Категории: streaming, social, video, database, store, radio, dj, international
    is_active = db.Column(db.Boolean, default=True)
    warning_message = db.Column(db.String(256), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), nullable=True)  # Иконка платформы
    
    @property
    def category_display(self):
        """Отображаемая категория"""
        categories = {
            'streaming': 'Стриминговые сервисы',
            'social': 'Социальные сети',
            'video': 'Видео платформы',
            'database': 'Музыкальные базы',
            'store': 'Магазины',
            'radio': 'Радио',
            'dj': 'DJ платформы',
            'international': 'Международные'
        }
        return categories.get(self.category, self.category)
    
    @staticmethod
    def get_default_platforms():
        """Получить список платформ по умолчанию"""
        return [
            # Стриминговые сервисы
            {'name': 'Spotify', 'category': 'streaming', 'sort_order': 1},
            {'name': 'Apple Music', 'category': 'streaming', 'sort_order': 2},
            {'name': 'Яндекс Музыка', 'category': 'streaming', 'sort_order': 3},
            {'name': 'VK Music', 'category': 'streaming', 'sort_order': 4},
            {'name': 'YouTube Music', 'category': 'streaming', 'sort_order': 5},
            {'name': 'Deezer', 'category': 'streaming', 'sort_order': 6},
            {'name': 'Zvooq', 'category': 'streaming', 'sort_order': 7},
            {'name': 'SberZvuk', 'category': 'streaming', 'sort_order': 8},
            {'name': 'Tidal', 'category': 'streaming', 'sort_order': 9},
            {'name': 'Amazon Music', 'category': 'streaming', 'sort_order': 10},
            # Социальные сети
            {'name': 'TikTok', 'category': 'social', 'sort_order': 20},
            {'name': 'Instagram/Facebook', 'category': 'social', 'sort_order': 21},
            {'name': 'Snapchat', 'category': 'social', 'sort_order': 22},
            # Видео
            {'name': 'YouTube Content ID', 'category': 'video', 'sort_order': 30},
            # Магазины
            {'name': 'iTunes', 'category': 'store', 'sort_order': 40},
            {'name': 'Google Play', 'category': 'store', 'sort_order': 41},
            # Базы данных
            {'name': 'Shazam', 'category': 'database', 'sort_order': 50},
            {'name': 'Genius', 'category': 'database', 'sort_order': 51},
        ]
    
    def __repr__(self):
        return f'<Platform {self.name}>'
