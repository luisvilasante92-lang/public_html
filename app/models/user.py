"""
Модель пользователя
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """Пользователи системы"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default='artist')  # admin, artist, label
    name = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(256), nullable=True)
    copyright = db.Column(db.String(256), nullable=True)
    partner_code = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)  # Телефон для SMS-кодов (формат 79XXXXXXXXX)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Налоговая и платёжная информация (редактирует пользователь только через поддержку; админ — в карточке пользователя)
    tax_status = db.Column(db.String(32), nullable=True)
    tax_legal_name = db.Column(db.String(512), nullable=True)
    tax_inn = db.Column(db.String(12), nullable=True)
    tax_bank_account = db.Column(db.String(32), nullable=True)
    tax_bank_name = db.Column(db.String(256), nullable=True)
    tax_bank_bik = db.Column(db.String(9), nullable=True)

    TAX_STATUS_CHOICES = (
        ('', 'Не указано'),
        ('self_employed', 'Самозанятый'),
        ('individual', 'Физическое лицо'),
        ('ip', 'Индивидуальный предприниматель (ИП)'),
        ('ooo', 'ООО'),
        ('zao', 'ЗАО'),
        ('other', 'Другое'),
    )
    
    # Связи
    releases = db.relationship('Release', backref='owner', lazy='dynamic')
    finances = db.relationship('Finance', backref='user', lazy='dynamic',
                               foreign_keys='Finance.user_id')
    tickets = db.relationship('Ticket', backref='user', lazy='dynamic')
    contracts = db.relationship('Contract', backref='user', lazy='dynamic',
                                foreign_keys='Contract.user_id')
    labels = db.relationship('Label', backref='user', lazy='dynamic')
    artists = db.relationship('Artist', backref='user', lazy='dynamic')
    smart_links = db.relationship('SmartLink', backref='user', lazy='dynamic')
    news = db.relationship('News', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        """Установить хеш пароля"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password, password)
    
    @property
    def is_admin(self):
        """Проверка на администратора"""
        return self.role == 'admin'
    
    @property
    def is_label(self):
        """Проверка на лейбл"""
        return self.role == 'label'
    
    @property
    def is_artist(self):
        """Проверка на артиста"""
        return self.role == 'artist'
    
    @property
    def display_name(self):
        """Отображаемое имя"""
        return self.name or self.login
    
    @property
    def avatar_url(self):
        """URL аватара"""
        if self.avatar:
            return f'/uploads/avatars/{self.avatar}'
        return '/static/img/default-avatar.png'
    
    def get_default_copyright(self):
        """Получить копирайт по умолчанию"""
        if self.copyright:
            return self.copyright
        return f'© {datetime.now().year} {self.name}'

    @classmethod
    def tax_status_labels(cls):
        return dict(cls.TAX_STATUS_CHOICES)

    @property
    def tax_status_display(self):
        if not self.tax_status:
            return 'Не указано'
        return self.tax_status_labels().get(self.tax_status, self.tax_status)

    def __repr__(self):
        return f'<User {self.login}>'
