"""
Договоры
"""

import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models.contract import Contract
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.files import save_file, delete_file, allowed_file
from app.utils.email import (
    send_contract_uploaded_email,
    send_contract_submitted_for_review_email,
    send_contract_approved_email,
    send_contract_rejected_email,
)

contracts_bp = Blueprint('contracts', __name__)


@contracts_bp.route('/contracts')
@login_required
def index():
    """Список договоров"""
    status = request.args.get('status', '')
    
    if current_user.is_admin:
        # Для админов - все договоры
        query = Contract.query
    else:
        # Для пользователей - только свои
        query = Contract.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    contracts = query.order_by(Contract.created_at.desc()).all()
    
    # Проверка просроченных договоров
    for contract in contracts:
        if contract.check_and_update_status():
            db.session.commit()
    
    # Количество по статусам
    if current_user.is_admin:
        counts = {
            'all': Contract.query.count(),
            'pending': Contract.query.filter_by(status='pending').count(),
            'pending_review': Contract.query.filter_by(status='pending_review').count(),
            'signed': Contract.query.filter_by(status='signed').count(),
            'expired': Contract.query.filter_by(status='expired').count(),
            'rejected': Contract.query.filter_by(status='rejected').count()
        }
    else:
        counts = {
            'all': Contract.query.filter_by(user_id=current_user.id).count(),
            'pending': Contract.query.filter_by(user_id=current_user.id, status='pending').count(),
            'pending_review': Contract.query.filter_by(user_id=current_user.id, status='pending_review').count(),
            'signed': Contract.query.filter_by(user_id=current_user.id, status='signed').count(),
            'expired': Contract.query.filter_by(user_id=current_user.id, status='expired').count(),
            'rejected': Contract.query.filter_by(user_id=current_user.id, status='rejected').count()
        }
    
    return render_template('contracts/index.html',
                          contracts=contracts,
                          status=status,
                          counts=counts)


@contracts_bp.route('/contracts/<int:id>')
@login_required
def view(id):
    """Просмотр договора"""
    contract = Contract.query.get_or_404(id)
    
    # Проверка доступа
    if not current_user.is_admin and contract.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('contracts.index'))
    
    # Проверка просрочки
    contract.check_and_update_status()
    db.session.commit()
    
    return render_template('contracts/view.html', contract=contract)


@contracts_bp.route('/contracts/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Создание договора (только админ)"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        user_id = request.form.get('user_id', type=int)
        deadline_str = request.form.get('sign_deadline', '')
        
        # Валидация
        if not title or not user_id:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('contracts.create'))
        
        user = User.query.get(user_id)
        if not user:
            flash('Пользователь не найден', 'error')
            return redirect(url_for('contracts.create'))
        
        # Загрузка файла
        pdf_file = request.files.get('file')
        if not pdf_file or not pdf_file.filename:
            flash('Загрузите PDF файл', 'error')
            return redirect(url_for('contracts.create'))
        
        if not allowed_file(pdf_file.filename, current_app.config['ALLOWED_CONTRACT_EXTENSIONS']):
            flash('Разрешены только PDF файлы', 'error')
            return redirect(url_for('contracts.create'))
        
        filename = save_file(pdf_file, 'contracts/original')
        if not filename:
            flash('Ошибка загрузки файла', 'error')
            return redirect(url_for('contracts.create'))
        
        # Парсинг дедлайна
        sign_deadline = None
        if deadline_str:
            try:
                sign_deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Создание договора
        contract = Contract(
            title=title,
            original_filename=pdf_file.filename,
            file_path=filename,
            user_id=user_id,
            admin_id=current_user.id,
            sign_deadline=sign_deadline,
            status='pending'
        )
        
        db.session.add(contract)
        db.session.commit()
        try:
            send_contract_uploaded_email(contract)
        except Exception as e:
            current_app.logger.warning('Не удалось отправить уведомление о договоре: %s', e)
        flash('Договор создан', 'success')
        return redirect(url_for('contracts.view', id=contract.id))
    
    # GET - форма
    users = User.query.filter(User.role != 'admin').order_by(User.name).all()
    return render_template('contracts/create.html', users=users)


@contracts_bp.route('/contracts/<int:id>/download')
@login_required
def download(id):
    """Скачивание договора"""
    contract = Contract.query.get_or_404(id)
    
    # Проверка доступа
    if not current_user.is_admin and contract.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('contracts.index'))
    
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'contracts', 'original')
    file_path = os.path.join(upload_folder, os.path.basename(contract.file_path))
    
    if not os.path.exists(file_path):
        flash('Файл не найден', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    return send_file(file_path, as_attachment=True,
                    download_name=contract.original_filename)


@contracts_bp.route('/contracts/<int:id>/download-signed')
@login_required
def download_signed(id):
    """Скачивание подписанного договора"""
    contract = Contract.query.get_or_404(id)
    
    # Проверка доступа
    if not current_user.is_admin and contract.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('contracts.index'))
    
    if not contract.signed_file_path:
        flash('Подписанный файл не найден', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'contracts', 'signed')
    file_path = os.path.join(upload_folder, os.path.basename(contract.signed_file_path))
    
    if not os.path.exists(file_path):
        flash('Файл не найден', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    return send_file(file_path, as_attachment=True,
                    download_name=contract.signed_filename or 'signed_contract.pdf')


@contracts_bp.route('/contracts/<int:id>/signed-preview')
@login_required
def signed_preview(id):
    """Отдача подписанного PDF для просмотра в браузере (вкладка / iframe), не как вложение."""
    contract = Contract.query.get_or_404(id)

    if not current_user.is_admin and contract.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('contracts.index'))

    if not contract.signed_file_path:
        flash('Подписанный файл не найден', 'error')
        return redirect(url_for('contracts.view', id=id))

    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'contracts', 'signed')
    file_path = os.path.join(upload_folder, os.path.basename(contract.signed_file_path))

    if not os.path.exists(file_path):
        flash('Файл не найден', 'error')
        return redirect(url_for('contracts.view', id=id))

    return send_file(
        file_path,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=contract.signed_filename or 'signed_contract.pdf',
    )


@contracts_bp.route('/contracts/<int:id>/sign', methods=['POST'])
@login_required
def sign(id):
    """Подписание договора"""
    contract = Contract.query.get_or_404(id)
    
    # Проверка доступа
    if contract.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('contracts.index'))
    
    # Проверка статуса
    if contract.status != 'pending':
        flash('Этот договор нельзя подписать', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    # Проверка просрочки
    if contract.is_expired:
        contract.status = 'expired'
        db.session.commit()
        flash('Срок подписания истёк', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    # Загрузка подписанного файла
    pdf_file = request.files.get('signed_file')
    if not pdf_file or not pdf_file.filename:
        flash('Загрузите подписанный PDF файл', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    if not allowed_file(pdf_file.filename, current_app.config['ALLOWED_CONTRACT_EXTENSIONS']):
        flash('Разрешены только PDF файлы', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    filename = save_file(pdf_file, 'contracts/signed')
    if not filename:
        flash('Ошибка загрузки файла', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    # Обновление договора: статус «на проверке», админ одобрит или отклонит
    contract.signed_filename = pdf_file.filename
    contract.signed_file_path = filename
    contract.signed_at = datetime.utcnow()
    contract.status = 'pending_review'
    
    db.session.commit()
    try:
        send_contract_submitted_for_review_email(contract)
    except Exception as e:
        current_app.logger.warning('Не удалось отправить уведомление: %s', e)
    
    flash('Договор отправлен на проверку. Мы свяжемся с вами в течение 3 рабочих дней.', 'success')
    return redirect(url_for('contracts.view', id=id))


@contracts_bp.route('/contracts/<int:id>/mark-signed', methods=['POST'])
@login_required
@admin_required
def mark_signed(id):
    """Отметить договор как подписанный (только админ): загрузить подписанный PDF и/или сменить статус."""
    contract = Contract.query.get_or_404(id)
    if contract.status not in ('pending', 'pending_review'):
        flash('Можно одобрить только договор со статусом «Ожидает подписания» или «На проверке»', 'error')
        return redirect(url_for('contracts.view', id=id))

    pdf_file = request.files.get('signed_file')
    if pdf_file and pdf_file.filename:
        if not allowed_file(pdf_file.filename, current_app.config['ALLOWED_CONTRACT_EXTENSIONS']):
            flash('Разрешены только PDF файлы', 'error')
            return redirect(url_for('contracts.view', id=id))
        filename = save_file(pdf_file, 'contracts/signed')
        if not filename:
            flash('Ошибка загрузки файла', 'error')
            return redirect(url_for('contracts.view', id=id))
        contract.signed_filename = pdf_file.filename
        contract.signed_file_path = filename
    contract.status = 'signed'
    contract.signed_at = contract.signed_at or datetime.utcnow()
    contract.rejection_reason = None
    db.session.commit()
    try:
        send_contract_approved_email(contract)
    except Exception as e:
        current_app.logger.warning('Не удалось отправить уведомление об одобрении: %s', e)
    flash('Договор одобрен и отмечен как подписанный', 'success')
    return redirect(url_for('contracts.view', id=id))


@contracts_bp.route('/contracts/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    """Отклонение договора. Админ может указать причину (обязательно для договора на проверке)."""
    contract = Contract.query.get_or_404(id)
    
    if contract.user_id != current_user.id and not current_user.is_admin:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('contracts.index'))
    
    if contract.status not in ('pending', 'pending_review'):
        flash('Этот договор нельзя отклонить', 'error')
        return redirect(url_for('contracts.view', id=id))

    reason = (request.form.get('rejection_reason') or '').strip()
    if contract.status == 'pending_review' and current_user.is_admin and not reason:
        flash('Укажите причину отклонения', 'error')
        return redirect(url_for('contracts.view', id=id))
    
    contract.status = 'rejected'
    contract.rejection_reason = reason if current_user.is_admin else None
    db.session.commit()
    if reason and contract.user and contract.user.email:
        try:
            send_contract_rejected_email(contract)
        except Exception as e:
            current_app.logger.warning('Не удалось отправить уведомление об отклонении: %s', e)
    
    flash('Договор отклонён', 'success')
    return redirect(url_for('contracts.view', id=id))


@contracts_bp.route('/contracts/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Удаление договора"""
    contract = Contract.query.get_or_404(id)
    
    # Удаление файлов
    if contract.file_path:
        delete_file(contract.file_path, 'contracts/original')
    if contract.signed_file_path:
        delete_file(contract.signed_file_path, 'contracts/signed')
    
    db.session.delete(contract)
    db.session.commit()
    
    flash('Договор удалён', 'success')
    return redirect(url_for('contracts.index'))
