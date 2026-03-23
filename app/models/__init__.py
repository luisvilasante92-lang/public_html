"""
Модели SQLAlchemy
"""

from app.models.user import User
from app.models.release import Release, Track, Platform
from app.models.analytics import ReleaseAnalytics, DeviceAnalytics, PlatformAnalytics, PlatformDailyListen
from app.models.finance import Finance, FinanceApproval, FinancePlatformLine
from app.models.news import News
from app.models.ticket import Ticket, TicketMessage
from app.models.notification import Notification
from app.models.contract import Contract
from app.models.smart_link import SmartLink, LinkVisit, LinkClick
from app.models.label import Label, Artist
from app.models.auth import AuthToken, LoginCode, RegistrationRequest
from app.models.pitch import Pitch
from app.models.auto_form import AutoFormRequest, AutoFormMessage
from app.models.video_request import VideoRequest
from app.models.knowledge_article import KnowledgeArticle
from app.models.knowledge_section import KnowledgeSection
from app.models.knowledge_topic import KnowledgeTopic

__all__ = [
    'User',
    'Release', 'Track', 'Platform',
    'ReleaseAnalytics', 'DeviceAnalytics', 'PlatformAnalytics', 'PlatformDailyListen',
    'Finance', 'FinanceApproval', 'FinancePlatformLine',
    'News',
    'Ticket', 'TicketMessage',
    'Notification',
    'Contract',
    'SmartLink', 'LinkVisit', 'LinkClick',
    'Label', 'Artist',
    'AuthToken', 'LoginCode', 'RegistrationRequest',
    'Pitch',
    'AutoFormRequest', 'AutoFormMessage',
    'VideoRequest',
    'KnowledgeArticle',
    'KnowledgeSection',
    'KnowledgeTopic',
]