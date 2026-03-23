"""
Главная страница (Dashboard)
"""

from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.news import News
from app.models.finance import Finance

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Главная страница дашборда"""
    # Получение последней новости
    latest_news = News.query.order_by(News.created_at.desc()).first()
    
    # Получение финансовых данных по кварталам текущего года
    current_year = datetime.now().year
    quarters_data = []
    
    if not current_user.is_admin:
        # Для пользователей - их данные
        for quarter in range(1, 5):
            finance = Finance.query.filter_by(
                user_id=current_user.id,
                year=current_year,
                quarter=quarter
            ).first()
            
            quarters_data.append({
                'quarter': quarter,
                'quarter_roman': ['I', 'II', 'III', 'IV'][quarter - 1],
                'amount': finance.amount if finance else None,
                'has_data': finance is not None
            })
    else:
        # Для админов - пустые данные
        for quarter in range(1, 5):
            quarters_data.append({
                'quarter': quarter,
                'quarter_roman': ['I', 'II', 'III', 'IV'][quarter - 1],
                'amount': None,
                'has_data': False
            })
    
    # Определение текущего квартала
    current_quarter = (datetime.now().month - 1) // 3 + 1
    
    # Статистика для артистов
    stats = {}
    if not current_user.is_admin:
        from app.models.release import Release
        stats = {
            'total_releases': Release.query.filter_by(user_id=current_user.id).count(),
            'approved_releases': Release.query.filter_by(
                user_id=current_user.id, status='approved'
            ).count(),
            'pending_releases': Release.query.filter_by(
                user_id=current_user.id, status='moderation'
            ).count(),
        }
    
    return render_template('dashboard/index.html',
                          latest_news=latest_news,
                          quarters_data=quarters_data,
                          current_quarter=current_quarter,
                          current_year=current_year,
                          stats=stats)
