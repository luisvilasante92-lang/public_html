"""
Авторизация
"""

from flask import Blueprint, redirect, url_for, request, flash, render_template, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from urllib.parse import urlparse
from app.models.auth import AuthToken, LoginCode
from app.models.user import User
from app.utils.email import send_login_code_email
from app.utils.sms import send_login_code_sms

auth_bp = Blueprint('auth', __name__)

# Email администратора: на него всегда отправляем и показываем коды входа (независимо от записи в БД)
ADMIN_EMAIL = 'press.saidman@gmail.com'


@auth_bp.route('/')
def index():
    """Главная страница - редирект на дашборд или авторизацию"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/faq')
def faq():
    """Страница «Часто задаваемые вопросы»"""
    return render_template('auth/faq.html')


@auth_bp.route('/login/forgot-password')
def forgot_password():
    """Напоминание о забытом пароле"""
    flash('Если вы забыли пароль, обратитесь в службу поддержки по электронной почте: support@lvr-music-publishing.ru. Либо на официальном сайте, в разделе «Контакты», в форме обратной связи.', 'support')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа — обычная форма логин/пароль"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        if not login_value or not password:
            flash('Введите логин и пароль', 'error')
            return render_template('auth/login.html')

        # Логин или email
        user = User.query.filter(
            (User.login == login_value) | (User.email == login_value)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Ваш аккаунт заблокирован', 'error')
                return render_template('auth/login.html')
            if not user.email and not user.phone:
                flash('В вашем аккаунте не указан email или телефон для получения кода. Обратитесь к администратору.', 'error')
                return render_template('auth/login.html')
            login_code = LoginCode.create_for_user(user.id)
            db.session.commit()
            sent_sms, sent_email = False, False
            recipient = ADMIN_EMAIL if user.role == 'admin' else None
            if user.email:
                ok, err_msg = send_login_code_email(user, login_code.code, recipient_override=recipient)
                sent_email = ok
            sms_err = None
            if user.phone:
                ok_sms, sms_err = send_login_code_sms(user.phone, login_code.code)
                sent_sms = ok_sms
            if sent_sms or sent_email:
                session['login_verify_user_id'] = user.id
                parts = []
                if sent_sms:
                    parts.append('телефон')
                if sent_email:
                    parts.append('почту')
                msg = f'Код подтверждения отправлен на {", ".join(parts)}. Введите его ниже.'
                if user.phone and not sent_sms and sms_err:
                    msg += f' (SMS не доставлено: {sms_err})'
                flash(msg, 'success' if sent_sms or sent_email else 'warning')
                return redirect(url_for('auth.login_verify'))
            if current_app.debug:
                session['login_verify_user_id'] = user.id
                flash(f'SMS и почта не настроены. Режим разработки — введите код: {login_code.code}', 'warning')
                return redirect(url_for('auth.login_verify'))
            flash('Укажите телефон или email в профиле для получения кода. Либо обратитесь к администратору.', 'error')

        else:
            flash('Неверный логин или пароль', 'error')

    return render_template('auth/login.html')


# Ключ в session для ожидания кода подтверждения входа
SESSION_LOGIN_VERIFY_USER_ID = 'login_verify_user_id'

# Минимальный интервал (секунды) между повторными отправками кода
LOGIN_CODE_RESEND_COOLDOWN = 60


@auth_bp.route('/login/verify', methods=['GET', 'POST'])
def login_verify():
    """Страница ввода кода подтверждения (после успешного логин/пароль)."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    user_id = session.get(SESSION_LOGIN_VERIFY_USER_ID)
    if not user_id:
        flash('Сначала введите логин и пароль', 'info')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user or not user.is_active:
        session.pop(SESSION_LOGIN_VERIFY_USER_ID, None)
        flash('Сессия входа истекла. Войдите снова.', 'error')
        return redirect(url_for('auth.login'))

    # Для администратора всегда показываем и отправляем код на ADMIN_EMAIL
    display_email = ADMIN_EMAIL if user.role == 'admin' else (user.email or '')

    if request.method == 'POST':
        code = (request.form.get('code') or '').strip().replace(' ', '')
        if len(code) != 5 or not code.isdigit():
            flash('Введите 5 цифр кода', 'error')
            return render_template('auth/login_verify.html', user=user, display_email=display_email)

        login_code = LoginCode.get_valid_for_user(user.id)
        if not login_code:
            flash('Код истёк или недействителен. Запросите новый код.', 'error')
            return render_template('auth/login_verify.html', user=user, display_email=display_email)

        if login_code.code != code:
            flash('Неверный код. Проверьте письмо и введите код ещё раз.', 'error')
            return render_template('auth/login_verify.html', user=user, display_email=display_email)

        session.pop(SESSION_LOGIN_VERIFY_USER_ID, None)

        # Редирект на ЛК (lk.luisv-records.ru): создаём токен и отправляем пользователя в callback
        callback_url = (current_app.config.get('AUTH_CALLBACK_URL') or '').strip()
        if callback_url:
            try:
                parsed = urlparse(callback_url)
                if parsed.netloc and parsed.netloc != request.host:
                    auth_token = AuthToken.create_for_user(user.id)
                    db.session.add(auth_token)
                    db.session.commit()
                    sep = '&' if '?' in callback_url else '?'
                    return redirect(f'{callback_url}{sep}token={auth_token.token}')
            except Exception:
                pass

        # Иначе остаёмся на auth (например, локальная разработка)
        login_user(user, remember=True)
        flash(f'Добро пожаловать, {user.display_name}!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login_verify.html', user=user, display_email=display_email)


@auth_bp.route('/login/verify/resend', methods=['POST'])
def login_verify_resend():
    """Повторная отправка кода подтверждения на почту."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    user_id = session.get(SESSION_LOGIN_VERIFY_USER_ID)
    if not user_id:
        flash('Сначала введите логин и пароль', 'info')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user or not user.is_active:
        session.pop(SESSION_LOGIN_VERIFY_USER_ID, None)
        flash('Сессия входа истекла. Войдите снова.', 'error')
        return redirect(url_for('auth.login'))

    from datetime import datetime, timedelta
    last = LoginCode.last_sent_at(user.id)
    if last and (datetime.utcnow() - last).total_seconds() < LOGIN_CODE_RESEND_COOLDOWN:
        flash('Новый код можно запросить через минуту после предыдущей отправки.', 'warning')
        return redirect(url_for('auth.login_verify'))

    login_code = LoginCode.create_for_user(user.id)
    db.session.commit()
    sent_sms, sent_email = False, False
    recipient = ADMIN_EMAIL if user.role == 'admin' else None
    if user.email:
        ok, err_msg = send_login_code_email(user, login_code.code, recipient_override=recipient)
        sent_email = ok
    if user.phone:
        ok_sms, _ = send_login_code_sms(user.phone, login_code.code)
        sent_sms = ok_sms
    if sent_sms or sent_email:
        parts = []
        if sent_sms:
            parts.append('телефон')
        if sent_email:
            parts.append('почту')
        flash(f'Новый код отправлен на {", ".join(parts)}.', 'success')
    else:
        flash('Не удалось отправить код. Проверьте настройки SMS и почты или попробуйте позже.', 'error')
    return redirect(url_for('auth.login_verify'))


@auth_bp.route('/auth/callback')
def callback():
    """Callback авторизации"""
    token_str = request.args.get('token')
    
    if not token_str:
        flash('Токен авторизации не предоставлен', 'error')
        return redirect(url_for('auth.login'))
    
    # Поиск токена в БД
    token = AuthToken.query.filter_by(token=token_str).first()
    
    if not token:
        flash('Недействительный токен авторизации', 'error')
        return redirect(url_for('auth.login'))
    
    # Проверка срока действия
    if token.is_expired:
        flash('Срок действия токена истек', 'error')
        return redirect(url_for('auth.login'))
    
    # Проверка, что токен не использован
    if token.is_used:
        flash('Токен уже был использован', 'error')
        return redirect(url_for('auth.login'))
    
    # Получение пользователя
    user = User.query.get(token.user_id)
    
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('auth.login'))
    
    if not user.is_active:
        flash('Ваш аккаунт заблокирован', 'error')
        return redirect(url_for('auth.login'))
    
    # Авторизация пользователя
    login_user(user, remember=True)
    
    # Помечаем токен как использованный
    token.mark_as_used()
    db.session.commit()
    
    flash(f'Добро пожаловать, {user.display_name}!', 'success')
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы. Редирект на auth.luisv-records.ru (страница входа), если сейчас на ЛК."""
    logout_user()
    flash('Вы вышли из системы', 'info')
    auth_url = (current_app.config.get('AUTH_SERVICE_URL') or '').strip().rstrip('/')
    if auth_url:
        try:
            parsed = urlparse(auth_url)
            if parsed.netloc and parsed.netloc != request.host:
                return redirect(f'{auth_url}/login')
        except Exception:
            pass
    return redirect(url_for('auth.login'))


# Для разработки - простая форма входа
@auth_bp.route('/dev-login', methods=['GET', 'POST'])
def dev_login():
    """Простая форма входа для разработки"""
    if not current_app.debug:
        return redirect(url_for('auth.login'))
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        user = User.query.filter_by(login=login).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Ваш аккаунт заблокирован', 'error')
                return render_template('auth/dev_login.html')
            
            login_user(user, remember=True)
            flash(f'Добро пожаловать, {user.display_name}!', 'success')
            return redirect(url_for('dashboard.index'))
        
        flash('Неверный логин или пароль', 'error')
    
    return render_template('auth/dev_login.html')


# Создание тестового пользователя для разработки
@auth_bp.route('/dev-setup')
def dev_setup():
    """Создание тестовых данных для разработки"""
    if not current_app.debug:
        return redirect(url_for('auth.login'))
    
    # Проверка, есть ли уже пользователи
    if User.query.count() > 0:
        flash('Тестовые данные уже созданы', 'info')
        return redirect(url_for('auth.dev_login'))
    
    # Создание администратора
    admin = User(
        login='admin',
        email='press.saidman@gmail.com',
        name='Администратор',
        role='admin'
    )
    admin.set_password('Admin123!')
    db.session.add(admin)
    
    # Создание артиста
    artist = User(
        login='artist',
        email='artist@example.com',
        name='Тестовый Артист',
        role='artist',
        copyright='© 2026 Тестовый Артист'
    )
    artist.set_password('Artist123!')
    db.session.add(artist)
    
    # Создание лейбла
    label = User(
        login='label',
        email='label@example.com',
        name='Тестовый Лейбл',
        role='label',
        copyright='© 2026 Test Records',
        partner_code='TEST001'
    )
    label.set_password('Label123!')
    db.session.add(label)
    
    # Создание платформ
    from app.models.release import Platform
    for platform_data in Platform.get_default_platforms():
        platform = Platform(**platform_data)
        db.session.add(platform)
    
    db.session.commit()
    
    flash('Тестовые данные созданы. Логины: admin, artist, label. Пароли: Admin123!, Artist123!, Label123!', 'success')
    return redirect(url_for('auth.dev_login'))


@auth_bp.route('/dev-update-admin-email')
def dev_update_admin_email():
    """Обновить email администратора на press.saidman@gmail.com (чтобы коды подтверждения приходили на нужную почту).
    Доступ: FLASK_DEBUG=1 или однократно ALLOW_UPDATE_ADMIN_EMAIL=1 на продакшене."""
    import os
    if not current_app.debug and os.environ.get('ALLOW_UPDATE_ADMIN_EMAIL') != '1':
        flash('Доступно только в режиме отладки или с ALLOW_UPDATE_ADMIN_EMAIL=1.', 'error')
        return redirect(url_for('auth.login'))
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        flash('Пользователь с ролью admin не найден.', 'error')
        return redirect(url_for('auth.login'))
    old_email = admin.email
    admin.email = ADMIN_EMAIL
    db.session.commit()
    flash(f'Email администратора обновлён: {old_email} → {ADMIN_EMAIL}', 'success')
    return redirect(url_for('auth.login'))
