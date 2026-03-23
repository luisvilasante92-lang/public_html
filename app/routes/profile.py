"""
Профиль пользователя
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.utils.files import save_file, delete_file, allowed_file
from app.utils.validators import validate_password
from app.utils.user_tax import apply_tax_fields_from_request
from app.models.user import User

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def index():
    """Профиль пользователя"""
    return render_template('profile/index.html')


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Редактирование профиля"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        copyright_text = request.form.get('copyright', '').strip()
        
        # Валидация email
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Этот email уже используется', 'error')
                return render_template('profile/edit.html')
        
        # Нормализация телефона (упрощённая: оставляем цифры, 79XXXXXXXXX)
        if phone:
            import re
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10 and digits.startswith('9'):
                phone = '7' + digits
            elif len(digits) == 11 and digits.startswith('7'):
                phone = digits
            elif len(digits) == 11 and digits.startswith('8'):
                phone = '7' + digits[1:]
            else:
                phone = digits if len(digits) >= 10 else None
        
        # Обновление данных
        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        current_user.copyright = copyright_text or None
        
        # Обновление аватара
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            if allowed_file(avatar_file.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
                # Удаление старого аватара
                if current_user.avatar:
                    delete_file(current_user.avatar, 'avatars')
                
                filename = save_file(avatar_file, 'avatars')
                if filename:
                    current_user.avatar = filename
            else:
                flash('Недопустимый формат аватара. Разрешены: JPG, PNG', 'error')
        
        db.session.commit()
        flash('Профиль обновлён', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html')


@profile_bp.route('/profile/tax-info/edit', methods=['GET', 'POST'])
@login_required
def tax_info_edit():
    """
    Налоговая информация: у артиста/лейбла — только через поддержку.
    Администратор может править свою карточку здесь; чужие — в разделе Пользователи.
    """
    if not current_user.is_admin:
        flash(
            'Изменить налоговую и платёжную информацию можно только через запрос в поддержку: '
            'создайте тикет и опишите, какие реквизиты нужно обновить.',
            'warning',
        )
        return redirect(url_for('profile.index'))

    if request.method == 'POST':
        apply_tax_fields_from_request(current_user, request.form)
        db.session.commit()
        flash('Налоговая и платёжная информация сохранена', 'success')
        return redirect(url_for('profile.index'))

    return render_template(
        'profile/tax_info.html',
        user=current_user,
        tax_choices=User.TAX_STATUS_CHOICES,
    )


@profile_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Смена пароля"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Проверка текущего пароля
        if not current_user.check_password(current_password):
            flash('Неверный текущий пароль', 'error')
            return render_template('profile/change_password.html')
        
        # Проверка совпадения паролей
        if new_password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('profile/change_password.html')
        
        # Валидация нового пароля
        password_errors = validate_password(new_password)
        if password_errors:
            for error in password_errors:
                flash(error, 'error')
            return render_template('profile/change_password.html')
        
        # Смена пароля
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Пароль успешно изменён', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/change_password.html')


@profile_bp.route('/profile/delete-avatar', methods=['POST'])
@login_required
def delete_avatar():
    """Удаление аватара"""
    if current_user.avatar:
        delete_file(current_user.avatar, 'avatars')
        current_user.avatar = None
        db.session.commit()
        flash('Аватар удалён', 'success')
    
    return redirect(url_for('profile.edit'))


@profile_bp.route('/uploads/avatars/<filename>')
@login_required
def serve_avatar(filename):
    """Отдача файла аватара"""
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'avatars')
    return send_file(os.path.join(upload_folder, filename))
