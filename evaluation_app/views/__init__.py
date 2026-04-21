from .home import index, set_language, about
from .auth_views import user_login, user_register, user_logout, user_dashboard
from .evaluation_views import (
    evaluation_list, evaluation_create, evaluation_update, evaluation_delete,
    evaluation_download_pdf, get_training_participants, get_available_participants,
)
from .professor_views import (
    professor_list, professor_create, professor_update, professor_delete, professor_download_pdf,
)
from .course_views import course_list, course_create, course_update, course_delete
from .participant_views import participant_list, participant_create, participant_update, participant_delete
from .location_views import location_list, location_create, location_update, location_delete
from .contact_views import contact, contact_list, contact_update, contact_delete
from .training_views import (
    train_list, train_create, train_update, train_delete, train_download_evaluations_pdf,
    train_participant_list, train_participant_create, train_participant_update, train_participant_delete,
)
from .system_views import system_closed, toggle_system_status, manage_system_settings
from .backup_views import (
    database_backup, database_backup_create, database_backup_restore,
    database_backup_download, database_backup_delete,
)
from .ai_views import (
    ai_chatbot, ai_professor_report, ai_dashboard_insights,
    ai_analyze_notes, ai_categorize_contact, ai_status,
)

__all__ = [
    'index', 'set_language', 'about',
    'user_login', 'user_register', 'user_logout', 'user_dashboard',
    'evaluation_list', 'evaluation_create', 'evaluation_update', 'evaluation_delete',
    'evaluation_download_pdf', 'get_training_participants', 'get_available_participants',
    'professor_list', 'professor_create', 'professor_update', 'professor_delete', 'professor_download_pdf',
    'course_list', 'course_create', 'course_update', 'course_delete',
    'participant_list', 'participant_create', 'participant_update', 'participant_delete',
    'location_list', 'location_create', 'location_update', 'location_delete',
    'contact', 'contact_list', 'contact_update', 'contact_delete',
    'train_list', 'train_create', 'train_update', 'train_delete', 'train_download_evaluations_pdf',
    'train_participant_list', 'train_participant_create', 'train_participant_update', 'train_participant_delete',
    'system_closed', 'toggle_system_status', 'manage_system_settings',
    'database_backup', 'database_backup_create', 'database_backup_restore',
    'database_backup_download', 'database_backup_delete',
    'ai_chatbot', 'ai_professor_report', 'ai_dashboard_insights',
    'ai_analyze_notes', 'ai_categorize_contact', 'ai_status',
]
