"""
Уведомления
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def index():
    """Список уведомлений"""
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .limit(100)\
        .all()
    return render_template('notifications/index.html', notifications=notifications)


@notifications_bp.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    """Отметить уведомление как прочитанное"""
    notif = Notification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    # Редирект на тикет, если есть, иначе на список уведомлений
    if notif.ticket_id:
        return redirect(url_for('tickets.view', id=notif.ticket_id))
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    """Отметить все уведомления как прочитанные"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return redirect(url_for('notifications.index'))
