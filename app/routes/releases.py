"""
Управление релизами
"""

import os
import csv
from io import StringIO
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, current_app, send_file, jsonify)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.release import Release, Track, Platform
from app.utils.files import save_file, delete_file, allowed_file
from app.utils.email import send_release_submitted_email

releases_bp = Blueprint('releases', __name__)


@releases_bp.route('/releases')
@login_required
def index():
    """Список релизов"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    # Базовый запрос
    query = Release.query.filter_by(user_id=current_user.id)
    
    # Фильтрация по статусу
    if status:
        query = query.filter_by(status=status)
    
    # Поиск по названию и артистам
    if search:
        query = query.filter(
            (Release.title.ilike(f'%{search}%')) |
            (Release.artists.ilike(f'%{search}%'))
        )
    
    # Сортировка и пагинация
    releases = query.order_by(Release.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get('RELEASES_PER_PAGE', 12),
        error_out=False
    )
    
    # Статусы для фильтра
    statuses = [
        ('', 'Все'),
        ('draft', 'Черновики'),
        ('moderation', 'На модерации'),
        ('approved', 'Одобренные'),
        ('rejected', 'Отклонённые'),
        ('deletion', 'На удалении')
    ]
    
    return render_template('releases/index.html',
                          releases=releases,
                          statuses=statuses,
                          current_status=status,
                          search=search)


@releases_bp.route('/releases/create', methods=['GET', 'POST'])
@login_required
def create():
    """Создание релиза"""
    if request.method == 'POST':
        # Получение данных формы
        title = request.form.get('title', '').strip()
        version = request.form.get('version', '').strip()
        artists = request.form.get('artists', '').strip()
        release_type = request.form.get('type', 'Single')
        genre = request.form.get('genre', '').strip()
        release_date_str = request.form.get('release_date', '')
        yandex_presave = request.form.get('yandex_presave') == 'on'
        upc = request.form.get('upc', '').strip() or None
        # Партнерский код, копирайт и платформы — из профиля / по умолчанию
        partner_code = current_user.partner_code
        copyright_text = current_user.get_default_copyright()
        platforms = [p.id for p in Platform.query.filter_by(is_active=True).order_by(Platform.sort_order).all()]
        
        # Валидация
        errors = []
        if not title:
            errors.append('Название релиза обязательно')
        if not artists:
            errors.append('Артисты обязательны')
        if not genre:
            errors.append('Жанр обязателен')
        if not release_date_str:
            errors.append('Дата релиза обязательна')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('releases/create.html', genres=current_app.config.get('RELEASE_GENRES', []))
        
        # Парсинг даты
        try:
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Неверный формат даты', 'error')
            return render_template('releases/create.html', genres=current_app.config.get('RELEASE_GENRES', []))
        
        # Создание релиза
        release = Release(
            user_id=current_user.id,
            title=title,
            version=version or None,
            artists=artists,
            type=release_type,
            genre=genre,
            release_date=release_date,
            yandex_presave=yandex_presave,
            upc=upc,
            partner_code=partner_code or current_user.partner_code,
            copyright=copyright_text or current_user.get_default_copyright(),
            platforms=platforms if platforms else None,
            status='draft'
        )
        
        # Загрузка обложки
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            if allowed_file(cover_file.filename, current_app.config['ALLOWED_COVER_EXTENSIONS']):
                filename = save_file(cover_file, 'covers')
                if filename:
                    release.cover = filename
            else:
                flash('Недопустимый формат обложки. Разрешены: JPG, PNG', 'error')
        
        db.session.add(release)
        db.session.commit()
        
        flash('Релиз создан. Добавьте треки и отправьте на модерацию.', 'success')
        return redirect(url_for('releases.edit', id=release.id))
    
    genres = current_app.config.get('RELEASE_GENRES', [])
    return render_template('releases/create.html', genres=genres)


@releases_bp.route('/releases/<int:id>')
@login_required
def view(id):
    """Просмотр релиза"""
    release = Release.query.get_or_404(id)
    
    # Проверка доступа
    if release.user_id != current_user.id and not current_user.is_admin:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('releases.index'))
    
    tracks = release.tracks.order_by(Track.track_order).all()
    
    return render_template('releases/view.html', release=release, tracks=tracks)


@releases_bp.route('/releases/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Редактирование релиза"""
    release = Release.query.get_or_404(id)
    
    # Проверка доступа
    if release.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('releases.index'))
    
    # Проверка возможности редактирования
    if not release.can_edit():
        flash('Этот релиз нельзя редактировать', 'error')
        return redirect(url_for('releases.view', id=id))
    
    if request.method == 'POST':
        # Обновление данных
        release.title = request.form.get('title', '').strip()
        release.version = request.form.get('version', '').strip() or None
        release.artists = request.form.get('artists', '').strip()
        release.type = request.form.get('type', 'Single')
        release.genre = request.form.get('genre', '').strip()
        release.yandex_presave = request.form.get('yandex_presave') == 'on'
        release.upc = request.form.get('upc', '').strip() or None
        # Партнерский код, копирайт, платформы — не меняются пользователем
        
        release_date_str = request.form.get('release_date', '')
        if release_date_str:
            try:
                release.release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Неверный формат даты', 'error')
        
        # Обновление обложки
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            if allowed_file(cover_file.filename, current_app.config['ALLOWED_COVER_EXTENSIONS']):
                # Удаление старой обложки
                if release.cover:
                    delete_file(release.cover, 'covers')
                
                filename = save_file(cover_file, 'covers')
                if filename:
                    release.cover = filename
            else:
                flash('Недопустимый формат обложки', 'error')
        
        db.session.commit()
        flash('Релиз обновлён', 'success')
        return redirect(url_for('releases.edit', id=id))
    
    tracks = release.tracks.order_by(Track.track_order).all()
    
    return render_template('releases/edit.html', release=release, tracks=tracks)


@releases_bp.route('/releases/<int:id>/submit', methods=['POST'])
@login_required
def submit(id):
    """Отправка релиза на модерацию"""
    release = Release.query.get_or_404(id)
    
    # Проверка доступа
    if release.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('releases.index'))
    
    # Проверка возможности отправки
    if not release.can_submit():
        if not release.cover:
            flash('Добавьте обложку релиза', 'error')
        elif release.tracks_count == 0:
            flash('Добавьте хотя бы один трек', 'error')
        else:
            flash('Этот релиз нельзя отправить на модерацию', 'error')
        return redirect(url_for('releases.edit', id=id))
    
    release.status = 'moderation'
    release.moderator_comment = None
    db.session.commit()

    try:
        ok = send_release_submitted_email(release)
        if not ok:
            flash('Релиз отправлен на модерацию. Уведомление на почту не отправлено — проверьте email в профиле и настройки SMTP в .env', 'warning')
    except Exception as e:
        current_app.logger.warning('Ошибка отправки уведомления о модерации: %s', e)
        flash('Релиз отправлен на модерацию. Не удалось отправить письмо на почту — проверьте настройки SMTP.', 'warning')

    flash('Релиз отправлен на модерацию', 'success')
    return redirect(url_for('releases.view', id=id))


@releases_bp.route('/releases/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Запрос на удаление релиза"""
    release = Release.query.get_or_404(id)
    
    # Проверка доступа
    if release.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('releases.index'))
    
    # Проверка возможности удаления
    if not release.can_delete():
        flash('Этот релиз нельзя удалить', 'error')
        return redirect(url_for('releases.view', id=id))
    
    if release.status == 'draft':
        # Черновик можно удалить сразу
        # Удаление файлов
        if release.cover:
            delete_file(release.cover, 'covers')
        
        for track in release.tracks:
            if track.wav_file:
                delete_file(track.wav_file, 'tracks')
        
        db.session.delete(release)
        db.session.commit()
        
        flash('Релиз удалён', 'success')
        return redirect(url_for('releases.index'))
    else:
        # Отправка запроса на удаление
        release.status = 'deletion'
        db.session.commit()
        
        flash('Запрос на удаление отправлен', 'info')
        return redirect(url_for('releases.view', id=id))


@releases_bp.route('/releases/<int:release_id>/tracks/add', methods=['POST'])
@login_required
def add_track(release_id):
    """Добавление трека"""
    release = Release.query.get_or_404(release_id)
    
    # Проверка доступа
    if release.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещён'}), 403
    
    if not release.can_edit():
        return jsonify({'error': 'Релиз нельзя редактировать'}), 400
    
    # Получение данных
    title = request.form.get('title', '').strip()
    artists = request.form.get('artists', '').strip()
    wav_file = request.files.get('wav_file')
    
    if not title or not artists:
        return jsonify({'error': 'Название и артисты обязательны'}), 400
    
    if not wav_file or not wav_file.filename:
        return jsonify({'error': 'WAV файл обязателен'}), 400
    
    if not allowed_file(wav_file.filename, current_app.config['ALLOWED_TRACK_EXTENSIONS']):
        return jsonify({'error': 'Разрешены только WAV файлы'}), 400
    
    # Сохранение файла
    filename = save_file(wav_file, 'tracks')
    if not filename:
        return jsonify({'error': 'Ошибка загрузки файла'}), 500
    
    # Определение порядка
    max_order = db.session.query(db.func.max(Track.track_order)).filter_by(
        release_id=release_id
    ).scalar() or 0
    
    # Создание трека
    track = Track(
        release_id=release_id,
        wav_file=filename,
        title=title,
        version=request.form.get('version', '').strip() or None,
        artists=artists,
        composers=request.form.get('composers', '').strip() or None,
        authors=request.form.get('authors', '').strip() or None,
        explicit=request.form.get('explicit') == 'on',
        language=request.form.get('language', '').strip() or None,
        isrc=request.form.get('isrc', '').strip() or None,
        lyrics=request.form.get('lyrics', '').strip() or None,
        track_order=max_order + 1
    )
    
    db.session.add(track)
    db.session.commit()
    
    flash('Трек добавлен', 'success')
    return redirect(url_for('releases.edit', id=release_id))


@releases_bp.route('/releases/<int:release_id>/tracks/<int:track_id>/edit', methods=['POST'])
@login_required
def edit_track(release_id, track_id):
    """Редактирование трека"""
    release = Release.query.get_or_404(release_id)
    track = Track.query.get_or_404(track_id)
    
    # Проверка доступа
    if release.user_id != current_user.id or track.release_id != release_id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('releases.edit', id=release_id))
    
    if not release.can_edit():
        flash('Релиз нельзя редактировать', 'error')
        return redirect(url_for('releases.edit', id=release_id))
    
    # Обновление данных
    track.title = request.form.get('title', '').strip()
    track.version = request.form.get('version', '').strip() or None
    track.artists = request.form.get('artists', '').strip()
    track.composers = request.form.get('composers', '').strip() or None
    track.authors = request.form.get('authors', '').strip() or None
    track.explicit = request.form.get('explicit') == 'on'
    track.language = request.form.get('language', '').strip() or None
    track.isrc = request.form.get('isrc', '').strip() or None
    track.lyrics = request.form.get('lyrics', '').strip() or None
    
    # Обновление WAV файла
    wav_file = request.files.get('wav_file')
    if wav_file and wav_file.filename:
        if allowed_file(wav_file.filename, current_app.config['ALLOWED_TRACK_EXTENSIONS']):
            # Удаление старого файла
            if track.wav_file:
                delete_file(track.wav_file, 'tracks')
            
            filename = save_file(wav_file, 'tracks')
            if filename:
                track.wav_file = filename
        else:
            flash('Разрешены только WAV файлы', 'error')
    
    db.session.commit()
    flash('Трек обновлён', 'success')
    return redirect(url_for('releases.edit', id=release_id))


@releases_bp.route('/releases/<int:release_id>/tracks/<int:track_id>/delete', methods=['POST'])
@login_required
def delete_track(release_id, track_id):
    """Удаление трека"""
    release = Release.query.get_or_404(release_id)
    track = Track.query.get_or_404(track_id)
    
    # Проверка доступа
    if release.user_id != current_user.id or track.release_id != release_id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('releases.edit', id=release_id))
    
    if not release.can_edit():
        flash('Релиз нельзя редактировать', 'error')
        return redirect(url_for('releases.edit', id=release_id))
    
    # Удаление файла
    if track.wav_file:
        delete_file(track.wav_file, 'tracks')
    
    db.session.delete(track)
    db.session.commit()
    
    flash('Трек удалён', 'success')
    return redirect(url_for('releases.edit', id=release_id))


@releases_bp.route('/releases/export')
@login_required
def export():
    """Экспорт каталога в CSV"""
    releases = Release.query.filter_by(user_id=current_user.id).order_by(Release.created_at.desc()).all()
    
    # Создание CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'ID', 'Название', 'Артисты', 'Тип', 'Жанр', 'Дата релиза',
        'Статус', 'UPC', 'Копирайт', 'Дата создания', 'Кол-во треков'
    ])
    
    # Данные
    for release in releases:
        writer.writerow([
            release.id,
            release.title,
            release.artists,
            release.type,
            release.genre,
            release.release_date.strftime('%d.%m.%Y'),
            release.status_display,
            release.upc or '',
            release.copyright or '',
            release.created_at.strftime('%d.%m.%Y'),
            release.tracks_count
        ])
    
    output.seek(0)
    
    # Отправка файла
    from io import BytesIO
    bytes_output = BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8-sig'))
    bytes_output.seek(0)
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'releases_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@releases_bp.route('/uploads/covers/<filename>')
@login_required
def serve_cover(filename):
    """Отдача файла обложки"""
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'covers')
    return send_file(os.path.join(upload_folder, filename))


@releases_bp.route('/uploads/tracks/<filename>')
@login_required
def serve_track(filename):
    """Отдача файла трека"""
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'tracks')
    return send_file(os.path.join(upload_folder, filename), as_attachment=True)
