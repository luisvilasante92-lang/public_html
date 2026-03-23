"""
Модели тикетов поддержки
"""

from datetime import datetime
from app import db


class Ticket(db.Model):
    """Тикеты поддержки"""
    
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject = db.Column(db.String(256), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open')  # open, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    messages = db.relationship('TicketMessage', backref='ticket', lazy='dynamic',
                               cascade='all, delete-orphan', order_by='TicketMessage.created_at')
    
    @property
    def display_id(self):
        """Отображаемый номер: AQL-0001, AQL-9583"""
        return f'AQL-{self.id:04d}'

    @property
    def status_display(self):
        """Отображаемый статус"""
        statuses = {
            'open': 'Открыт',
            'closed': 'Закрыт'
        }
        return statuses.get(self.status, self.status)
    
    @property
    def status_class(self):
        """CSS класс для статуса"""
        return 'status-open' if self.status == 'open' else 'status-closed'
    
    @property
    def messages_count(self):
        """Количество сообщений"""
        return self.messages.count()
    
    @property
    def last_message(self):
        """Последнее сообщение"""
        return self.messages.order_by(TicketMessage.created_at.desc()).first()
    
    @property
    def is_open(self):
        """Тикет открыт"""
        return self.status == 'open'
    
    def __repr__(self):
        return f'<Ticket {self.id}: {self.subject}>'


class TicketMessage(db.Model):
    """Сообщения в тикетах"""
    
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи
    author = db.relationship('User', foreign_keys=[user_id])
    
    @property
    def time_formatted(self):
        """Форматированное время"""
        return self.created_at.strftime('%d.%m.%Y %H:%M')
    
    def __repr__(self):
        return f'<TicketMessage {self.id}>'
