"""
Тикеты поддержки
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.ticket import Ticket, TicketMessage
from app.models.notification import Notification
from app.utils.decorators import admin_required

tickets_bp = Blueprint('tickets', __name__)


def _get_tickets_sidebar(current_user, status=''):
    """Тикеты для левой панели (без пагинации, последние 50)"""
    if current_user.is_admin:
        query = Ticket.query
    else:
        query = Ticket.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Ticket.updated_at.desc()).limit(50).all()


@tickets_bp.route('/tickets')
@login_required
def index():
    """Поддержка: левая панель — архив, правая — выбор обращения"""
    status = request.args.get('status', '')
    tickets_list = _get_tickets_sidebar(current_user, status)
    if current_user.is_admin:
        counts = {
            'all': Ticket.query.count(),
            'open': Ticket.query.filter_by(status='open').count(),
            'closed': Ticket.query.filter_by(status='closed').count()
        }
    else:
        counts = {
            'all': Ticket.query.filter_by(user_id=current_user.id).count(),
            'open': Ticket.query.filter_by(user_id=current_user.id, status='open').count(),
            'closed': Ticket.query.filter_by(user_id=current_user.id, status='closed').count()
        }
    return render_template('tickets/inbox.html',
                          tickets_list=tickets_list,
                          selected_ticket=None,
                          messages=[],
                          status=status,
                          counts=counts)


@tickets_bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create():
    """Создание тикета"""
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Валидация
        if not subject or not message:
            flash('Заполните все обязательные поля', 'error')
            return render_template('tickets/create.html')
        
        # Создание тикета
        ticket = Ticket(
            user_id=current_user.id,
            subject=subject,
            message=message,
            status='open'
        )
        
        db.session.add(ticket)
        db.session.commit()

        # Уведомление автору о создании тикета
        notif = Notification(
            user_id=current_user.id,
            kind='ticket_created',
            title='Тикет создан',
            message=f'Ваш тикет «{ticket.subject}» успешно создан.',
            ticket_id=ticket.id
        )
        db.session.add(notif)
        db.session.commit()

        # Email исполнителям и автору о принятии тикета в работу
        from app.utils.email import send_ticket_accepted_email, send_ticket_confirmation_to_author
        try:
            send_ticket_accepted_email(ticket)
        except Exception as e:
            current_app.logger.warning('Ошибка отправки тикета исполнителям: %s', e)
        author_email_ok = False
        try:
            author_email_ok = send_ticket_confirmation_to_author(ticket)
        except Exception as e:
            current_app.logger.warning('Ошибка отправки подтверждения автору: %s', e)

        flash('Тикет %s создан' % ticket.display_id, 'success')
        if not author_email_ok:
            flash('Подтверждение на почту не отправлено. Проверьте email в профиле и настройки SMTP в .env', 'warning')
        return redirect(url_for('tickets.view', id=ticket.id))
    
    return render_template('tickets/create.html')


@tickets_bp.route('/tickets/<int:id>')
@login_required
def view(id):
    """Просмотр тикета: левая панель — архив, правая — чат"""
    ticket = Ticket.query.get_or_404(id)

    # Проверка доступа
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('tickets.index'))

    # Пометить уведомления по этому тикету как прочитанные
    Notification.query.filter_by(
        user_id=current_user.id, ticket_id=ticket.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()

    messages = ticket.messages.order_by(TicketMessage.created_at).all()
    tickets_list = _get_tickets_sidebar(current_user, '')
    if current_user.is_admin:
        counts = {
            'all': Ticket.query.count(),
            'open': Ticket.query.filter_by(status='open').count(),
            'closed': Ticket.query.filter_by(status='closed').count()
        }
    else:
        counts = {
            'all': Ticket.query.filter_by(user_id=current_user.id).count(),
            'open': Ticket.query.filter_by(user_id=current_user.id, status='open').count(),
            'closed': Ticket.query.filter_by(user_id=current_user.id, status='closed').count()
        }

    return render_template('tickets/inbox.html',
                          tickets_list=tickets_list,
                          selected_ticket=ticket,
                          messages=messages,
                          status='',
                          counts=counts)


@tickets_bp.route('/tickets/<int:id>/reply', methods=['POST'])
@login_required
def reply(id):
    """Ответ в тикете"""
    ticket = Ticket.query.get_or_404(id)
    
    # Проверка доступа
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('tickets.index'))
    
    message_text = request.form.get('message', '').strip()
    
    if not message_text:
        flash('Сообщение не может быть пустым', 'error')
        return redirect(url_for('tickets.view', id=id))
    
    # Создание сообщения
    message = TicketMessage(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=message_text,
        is_admin=current_user.is_admin
    )
    
    db.session.add(message)
    
    # Открытие тикета при ответе пользователя
    if not current_user.is_admin and ticket.status == 'closed':
        ticket.status = 'open'

    db.session.commit()

    # Уведомление владельцу тикета о новом ответе (если ответил не он)
    if ticket.user_id != current_user.id:
        reply_notif = Notification(
            user_id=ticket.user_id,
            kind='ticket_reply',
            title='Новый ответ в тикете',
            message=f'В тикете «{ticket.subject}» новый ответ.',
            ticket_id=ticket.id
        )
        db.session.add(reply_notif)
        db.session.commit()

        # Email автору, если ответил админ
        if current_user.is_admin:
            try:
                db.session.refresh(ticket)  # обновить связь user после commit
                from app.utils.email import send_ticket_reply_email
                ok = send_ticket_reply_email(ticket, message_text)
                if not ok:
                    flash('Уведомление на почту автору не отправлено', 'warning')
            except Exception as e:
                current_app.logger.warning('Ошибка отправки email об ответе: %s', e)
                flash(f'Ошибка отправки email: {e}', 'warning')

    flash('Сообщение отправлено', 'success')
    return redirect(url_for('tickets.view', id=id))


@tickets_bp.route('/tickets/<int:id>/close', methods=['POST'])
@login_required
def close(id):
    """Закрытие тикета"""
    ticket = Ticket.query.get_or_404(id)
    
    # Проверка доступа
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('tickets.index'))
    
    ticket.status = 'closed'
    db.session.commit()

    # Уведомление владельцу тикета о закрытии
    if ticket.user_id != current_user.id:
        close_notif = Notification(
            user_id=ticket.user_id,
            kind='ticket_closed',
            title='Тикет закрыт',
            message=f'Тикет «{ticket.subject}» закрыт.',
            ticket_id=ticket.id
        )
        db.session.add(close_notif)
        db.session.commit()

        # Email автору о закрытии (когда закрыл админ)
        if current_user.is_admin:
            try:
                db.session.refresh(ticket)  # обновить связь user после commit
                from app.utils.email import send_ticket_closed_email
                ok = send_ticket_closed_email(ticket)
                if not ok:
                    flash('Уведомление на почту автору не отправлено', 'warning')
            except Exception as e:
                current_app.logger.warning('Ошибка отправки email о закрытии: %s', e)
                flash(f'Ошибка отправки email: {e}', 'warning')
    else:
        # Автор закрыл свой тикет — тоже уведомление для истории
        close_notif = Notification(
            user_id=current_user.id,
            kind='ticket_closed',
            title='Тикет закрыт',
            message=f'Тикет «{ticket.subject}» закрыт.',
            ticket_id=ticket.id
        )
        db.session.add(close_notif)
        db.session.commit()

    flash('Тикет закрыт', 'success')
    return redirect(url_for('tickets.view', id=id))


@tickets_bp.route('/tickets/<int:id>/open', methods=['POST'])
@login_required
@admin_required
def reopen(id):
    """Открытие тикета (только админ)"""
    ticket = Ticket.query.get_or_404(id)
    
    ticket.status = 'open'
    db.session.commit()
    
    flash('Тикет открыт', 'success')
    return redirect(url_for('tickets.view', id=id))


@tickets_bp.route('/tickets/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Удаление тикета"""
    ticket = Ticket.query.get_or_404(id)
    
    db.session.delete(ticket)
    db.session.commit()
    
    flash('Тикет удалён', 'success')
    return redirect(url_for('tickets.index'))
