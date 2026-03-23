"""
Модерация релизов (только для админов)
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models.release import Release, Track
from app.utils.decorators import admin_required
from app.utils.files import delete_file
from app.utils.email import send_release_approved_email, send_release_rejected_email

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/moderation')
@login_required
@admin_required
def index():
    """Список релизов на модерации"""
    tab = request.args.get('tab', 'moderation')
    page = request.args.get('page', 1, type=int)
    
    # Определение статуса по вкладке
    status_map = {
        'moderation': 'moderation',
        'approved': 'approved',
        'deletion': 'deletion'
    }
    
    status = status_map.get(tab, 'moderation')
    
    # Запрос релизов
    releases = Release.query.filter_by(status=status).order_by(
        Release.created_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config.get('RELEASES_PER_PAGE', 12),
        error_out=False
    )
    
    # Количество по статусам
    counts = {
        'moderation': Release.query.filter_by(status='moderation').count(),
        'approved': Release.query.filter_by(status='approved').count(),
        'deletion': Release.query.filter_by(status='deletion').count()
    }
    
    return render_template('moderation/index.html',
                          releases=releases,
                          tab=tab,
                          counts=counts)


@moderation_bp.route('/moderation/<int:id>')
@login_required
@admin_required
def view(id):
    """Просмотр релиза на модерации"""
    release = Release.query.get_or_404(id)
    tracks = release.tracks.order_by(Track.track_order).all()
    
    return render_template('moderation/view.html', release=release, tracks=tracks)


@moderation_bp.route('/moderation/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve(id):
    """Одобрение релиза"""
    release = Release.query.get_or_404(id)
    
    if release.status != 'moderation':
        flash('Этот релиз не находится на модерации', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    # UPC код (опционально)
    upc = request.form.get('upc', '').strip()
    if upc:
        release.upc = upc
    
    release.status = 'approved'
    release.moderator_comment = None
    db.session.commit()

    try:
        ok = send_release_approved_email(release)
        if not ok:
            flash('Релиз одобрен. Уведомление артисту на почту не отправлено — проверьте email в профиле артиста и настройки SMTP.', 'warning')
    except Exception as e:
        current_app.logger.warning('Ошибка отправки уведомления об одобрении: %s', e)
        flash('Релиз одобрен. Не удалось отправить письмо артисту — проверьте настройки SMTP.', 'warning')

    flash('Релиз одобрен', 'success')
    return redirect(url_for('moderation.index'))


@moderation_bp.route('/moderation/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject(id):
    """Отклонение релиза"""
    release = Release.query.get_or_404(id)
    
    if release.status != 'moderation':
        flash('Этот релиз не находится на модерации', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    comment = request.form.get('comment', '').strip()
    if not comment:
        flash('Укажите причину отклонения', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    release.status = 'rejected'
    release.moderator_comment = comment
    db.session.commit()

    try:
        ok = send_release_rejected_email(release)
        if not ok:
            flash('Релиз отклонён. Уведомление артисту на почту не отправлено — проверьте email в профиле артиста и настройки SMTP.', 'warning')
    except Exception as e:
        current_app.logger.warning('Ошибка отправки уведомления об отклонении: %s', e)
        flash('Релиз отклонён. Не удалось отправить письмо артисту — проверьте настройки SMTP.', 'warning')

    flash('Релиз отклонён', 'success')
    return redirect(url_for('moderation.index'))


@moderation_bp.route('/moderation/<int:id>/confirm-delete', methods=['POST'])
@login_required
@admin_required
def confirm_delete(id):
    """Подтверждение удаления релиза"""
    release = Release.query.get_or_404(id)
    
    if release.status != 'deletion':
        flash('Этот релиз не ожидает удаления', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    # Удаление файлов
    if release.cover:
        delete_file(release.cover, 'covers')
    
    for track in release.tracks:
        if track.wav_file:
            delete_file(track.wav_file, 'tracks')
    
    # Удаление из БД
    db.session.delete(release)
    db.session.commit()
    
    flash('Релиз удалён', 'success')
    return redirect(url_for('moderation.index', tab='deletion'))


@moderation_bp.route('/moderation/<int:id>/cancel-delete', methods=['POST'])
@login_required
@admin_required
def cancel_delete(id):
    """Отмена удаления релиза"""
    release = Release.query.get_or_404(id)
    
    if release.status != 'deletion':
        flash('Этот релиз не ожидает удаления', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    release.status = 'approved'
    db.session.commit()
    
    flash('Запрос на удаление отменён', 'success')
    return redirect(url_for('moderation.index', tab='deletion'))


@moderation_bp.route('/moderation/<int:id>/update-upc', methods=['POST'])
@login_required
@admin_required
def update_upc(id):
    """Обновление UPC кода"""
    release = Release.query.get_or_404(id)
    
    upc = request.form.get('upc', '').strip()
    release.upc = upc if upc else None
    db.session.commit()
    
    flash('UPC код обновлён', 'success')
    return redirect(url_for('moderation.view', id=id))


@moderation_bp.route('/moderation/<int:id>/download-cover')
@login_required
@admin_required
def download_cover(id):
    """Скачивание обложки"""
    release = Release.query.get_or_404(id)
    
    if not release.cover:
        flash('Обложка не найдена', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'covers')
    file_path = os.path.join(upload_folder, release.cover)
    
    if not os.path.exists(file_path):
        flash('Файл не найден', 'error')
        return redirect(url_for('moderation.view', id=id))
    
    return send_file(file_path, as_attachment=True,
                    download_name=f'{release.title}_cover{os.path.splitext(release.cover)[1]}')


@moderation_bp.route('/moderation/<int:release_id>/track/<int:track_id>/set-isrc', methods=['POST'])
@login_required
@admin_required
def set_track_isrc(release_id, track_id):
    """Установка или изменение ISRC кода трека (админ)"""
    release = Release.query.get_or_404(release_id)
    track = Track.query.get_or_404(track_id)
    if track.release_id != release_id:
        flash('Трек не принадлежит этому релизу', 'error')
        return redirect(url_for('moderation.view', id=release_id))
    isrc = request.form.get('isrc', '').strip().replace(' ', '').upper() or None
    if isrc:
        from app.utils.validators import validate_isrc
        if not validate_isrc(isrc):
            flash(f'Неверный формат ISRC для трека «{track.title}». Ожидается: CCXXXYYNNNNN (например RUABC1234567)', 'error')
            return redirect(url_for('moderation.view', id=release_id))
    track.isrc = isrc
    db.session.commit()
    flash('ISRC код сохранён', 'success')
    return redirect(url_for('moderation.view', id=release_id))


@moderation_bp.route('/moderation/<int:release_id>/download-track/<int:track_id>')
@login_required
@admin_required
def download_track(release_id, track_id):
    """Скачивание трека"""
    release = Release.query.get_or_404(release_id)
    track = Track.query.get_or_404(track_id)
    
    if track.release_id != release_id:
        flash('Трек не принадлежит этому релизу', 'error')
        return redirect(url_for('moderation.view', id=release_id))
    
    if not track.wav_file:
        flash('Файл не найден', 'error')
        return redirect(url_for('moderation.view', id=release_id))
    
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'tracks')
    file_path = os.path.join(upload_folder, track.wav_file)
    
    if not os.path.exists(file_path):
        flash('Файл не найден', 'error')
        return redirect(url_for('moderation.view', id=release_id))
    
    return send_file(file_path, as_attachment=True,
                    download_name=f'{track.title}.wav')
