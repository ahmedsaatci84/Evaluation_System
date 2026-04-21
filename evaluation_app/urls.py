from django.urls import path
from .views import (
    # Home
    index, set_language, about,
    # Auth
    user_login, user_register, user_logout, user_dashboard,
    # Evaluations
    evaluation_list, evaluation_create, evaluation_update, evaluation_delete,
    evaluation_download_pdf, get_training_participants, get_available_participants,
    # Professors
    professor_list, professor_create, professor_update, professor_delete, professor_download_pdf,
    # Courses
    course_list, course_create, course_update, course_delete,
    # Participants
    participant_list, participant_create, participant_update, participant_delete,
    # Locations
    location_list, location_create, location_update, location_delete,
    # Contact
    contact, contact_list, contact_update, contact_delete,
    # Training sessions
    train_list, train_create, train_update, train_delete, train_download_evaluations_pdf,
    # Training participants
    train_participant_list, train_participant_create, train_participant_update, train_participant_delete,
    # System
    system_closed, toggle_system_status, manage_system_settings,
    # Backup
    database_backup, database_backup_create, database_backup_restore,
    database_backup_download, database_backup_delete,
    # AI
    ai_chatbot, ai_professor_report, ai_dashboard_insights,
    ai_analyze_notes, ai_categorize_contact, ai_status,
)

urlpatterns = [
    # Home & pages
    path('', index, name='home'),
    path('set-language/', set_language, name='set_language'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),

    # Authentication
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', user_dashboard, name='dashboard'),

    # Contact messages
    path('contacts/', contact_list, name='contact_list'),
    path('contacts/<int:pk>/update/', contact_update, name='contact_update'),
    path('contacts/<int:pk>/delete/', contact_delete, name='contact_delete'),

    # Evaluations
    path('evaluations/', evaluation_list, name='evaluation_list'),
    path('evaluations/create/', evaluation_create, name='evaluation_create'),
    path('evaluations/<int:pk>/update/', evaluation_update, name='evaluation_update'),
    path('evaluations/<int:pk>/delete/', evaluation_delete, name='evaluation_delete'),
    path('evaluations/<int:pk>/download-pdf/', evaluation_download_pdf, name='evaluation_download_pdf'),
    path('api/training/<int:train_id>/participants/', get_training_participants, name='get_training_participants'),
    path('api/training/<int:train_id>/available-participants/', get_available_participants, name='get_available_participants'),

    # Professors
    path('professors/', professor_list, name='professor_list'),
    path('professors/create/', professor_create, name='professor_create'),
    path('professors/<int:pk>/update/', professor_update, name='professor_update'),
    path('professors/<int:pk>/delete/', professor_delete, name='professor_delete'),
    path('professors/<int:pk>/download-pdf/', professor_download_pdf, name='professor_download_pdf'),

    # Courses
    path('courses/', course_list, name='course_list'),
    path('courses/create/', course_create, name='course_create'),
    path('courses/<int:pk>/update/', course_update, name='course_update'),
    path('courses/<int:pk>/delete/', course_delete, name='course_delete'),

    # Participants
    path('participants/', participant_list, name='participant_list'),
    path('participants/create/', participant_create, name='participant_create'),
    path('participants/<int:pk>/update/', participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', participant_delete, name='participant_delete'),

    # Locations
    path('locations/', location_list, name='location_list'),
    path('locations/create/', location_create, name='location_create'),
    path('locations/<int:pk>/update/', location_update, name='location_update'),
    path('locations/<int:pk>/delete/', location_delete, name='location_delete'),

    # Training sessions
    path('training/', train_list, name='train_list'),
    path('training/create/', train_create, name='train_create'),
    path('training/<int:pk>/update/', train_update, name='train_update'),
    path('training/<int:pk>/delete/', train_delete, name='train_delete'),
    path('training/<int:pk>/download-evaluations-pdf/', train_download_evaluations_pdf, name='train_download_evaluations_pdf'),

    # Training participants
    path('training-participants/', train_participant_list, name='train_participant_list'),
    path('training-participants/create/', train_participant_create, name='train_participant_create'),
    path('training-participants/<int:pk>/update/', train_participant_update, name='train_participant_update'),
    path('training-participants/<int:pk>/delete/', train_participant_delete, name='train_participant_delete'),

    # System management
    path('system-closed/', system_closed, name='system_closed'),
    path('toggle-system-status/', toggle_system_status, name='toggle_system_status'),
    path('system-settings/', manage_system_settings, name='manage_system_settings'),

    # Database backup (admin only)
    path('database-backup/', database_backup, name='database_backup'),
    path('database-backup/create/', database_backup_create, name='database_backup_create'),
    path('database-backup/restore/<str:filename>/', database_backup_restore, name='database_backup_restore'),
    path('database-backup/download/<str:filename>/', database_backup_download, name='database_backup_download'),
    path('database-backup/delete/<str:filename>/', database_backup_delete, name='database_backup_delete'),

    # AI assistant
    path('ai/chatbot/', ai_chatbot, name='ai_chatbot'),
    path('ai/professor/<int:pk>/report/', ai_professor_report, name='ai_professor_report'),
    path('ai/dashboard/insights/', ai_dashboard_insights, name='ai_dashboard_insights'),
    path('ai/analyze-notes/', ai_analyze_notes, name='ai_analyze_notes'),
    path('ai/contact/<int:pk>/categorize/', ai_categorize_contact, name='ai_categorize_contact'),
    path('ai/status/', ai_status, name='ai_status'),
]
