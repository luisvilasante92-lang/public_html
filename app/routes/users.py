"""
Управление пользователями (только админ)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.user_tax import apply_tax_fields_from_request
from app.utils.validators import validate_password

users_bp = Blueprint('users', __name__)


@users_bp.route('/users')
@login_required
@admin_required
def index():
    """Список пользователей"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    # Фильтрация по роли
    if role:
        query = query.filter_by(role=role)
    
    # Фильтрация по статусу
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'blocked':
        query = query.filter_by(is_active=False)
    
    # Поиск
    if search:
        query = query.filter(
            (User.login.ilike(f'%{search}%')) |
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get('USERS_PER_PAGE', 20),
        error_out=False
    )
    
    # Количество по ролям
    counts = {
        'all': User.query.count(),
        'admin': User.query.filter_by(role='admin').count(),
        'artist': User.query.filter_by(role='artist').count(),
        'label': User.query.filter_by(role='label').count()
    }
    
    return render_template('users/index.html',
                          users=users,
                          role=role,
                          status=status,
                          search=search,
                          counts=counts)


@users_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Создание пользователя"""
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'artist')
        password = request.form.get('password', '')
        copyright_text = request.form.get('copyright', '').strip()
        partner_code = request.form.get('partner_code', '').strip()
        
        # Валидация
        errors = []
        
        if not login:
            errors.append('Логин обязателен')
        elif User.query.filter_by(login=login).first():
            errors.append('Пользователь с таким логином уже существует')
        
        if not email:
            errors.append('Email обязателен')
        elif User.query.filter_by(email=email).first():
            errors.append('Пользователь с таким email уже существует')
        
        if not name:
            errors.append('Имя обязательно')
        
        if not password:
            errors.append('Пароль обязателен')
        else:
            password_errors = validate_password(password)
            errors.extend(password_errors)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('users/create.html')
        
        # Создание пользователя
        user = User(
            login=login,
            email=email,
            name=name,
            role=role,
            copyright=copyright_text or None,
            partner_code=partner_code if role == 'label' else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Пользователь создан', 'success')
        return redirect(url_for('users.view', id=user.id))
    
    return render_template('users/create.html')


@users_bp.route('/users/<int:id>')
@login_required
@admin_required
def view(id):
    """Просмотр пользователя"""
    user = User.query.get_or_404(id)
    
    # Статистика
    stats = {
        'releases_count': user.releases.count(),
        'approved_releases': user.releases.filter_by(status='approved').count(),
        'tickets_count': user.tickets.count(),
        'contracts_count': user.contracts.count()
    }
    
    return render_template('users/view.html', user=user, stats=stats)


@users_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Редактирование пользователя"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        # Обновление данных
        new_login = request.form.get('login', '').strip()
        new_email = request.form.get('email', '').strip()
        
        # Проверка уникальности
        if new_login != user.login:
            if User.query.filter_by(login=new_login).first():
                flash('Пользователь с таким логином уже существует', 'error')
                return render_template(
                    'users/edit.html', user=user, tax_choices=User.TAX_STATUS_CHOICES
                )

        if new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Пользователь с таким email уже существует', 'error')
                return render_template(
                    'users/edit.html', user=user, tax_choices=User.TAX_STATUS_CHOICES
                )
        
        user.login = new_login
        user.email = new_email
        user.name = request.form.get('name', '').strip()
        user.role = request.form.get('role', 'artist')
        user.copyright = request.form.get('copyright', '').strip() or None
        user.partner_code = request.form.get('partner_code', '').strip() if user.role == 'label' else None

        apply_tax_fields_from_request(user, request.form)

        # Смена пароля (если указан)
        new_password = request.form.get('password', '')
        if new_password:
            password_errors = validate_password(new_password)
            if password_errors:
                for error in password_errors:
                    flash(error, 'error')
                return render_template(
                    'users/edit.html', user=user, tax_choices=User.TAX_STATUS_CHOICES
                )
            user.set_password(new_password)

        db.session.commit()
        flash('Пользователь обновлён', 'success')
        return redirect(url_for('users.view', id=id))
    
    return render_template(
        'users/edit.html', user=user, tax_choices=User.TAX_STATUS_CHOICES
    )


@users_bp.route('/users/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(id):
    """Блокировка/разблокировка пользователя"""
    user = User.query.get_or_404(id)
    
    # Нельзя блокировать себя
    if user.id == current_user.id:
        flash('Вы не можете заблокировать себя', 'error')
        return redirect(url_for('users.view', id=id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    if user.is_active:
        flash('Пользователь разблокирован', 'success')
    else:
        flash('Пользователь заблокирован', 'success')
    
    return redirect(url_for('users.view', id=id))


@users_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Удаление пользователя"""
    user = User.query.get_or_404(id)
    
    # Нельзя удалить себя
    if user.id == current_user.id:
        flash('Вы не можете удалить себя', 'error')
        return redirect(url_for('users.view', id=id))
    
    # Проверка наличия связанных данных
    if user.releases.count() > 0:
        flash('Нельзя удалить пользователя с релизами', 'error')
        return redirect(url_for('users.view', id=id))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Пользователь удалён', 'success')
    return redirect(url_for('users.index'))
