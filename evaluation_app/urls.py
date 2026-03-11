from django.urls import path
from . import views
from . import ai_views

urlpatterns = [
    path('', views.index, name='home'),
    path('set-language/', views.set_language, name='set_language'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    
    # Contact Message URLs
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/<int:pk>/update/', views.contact_update, name='contact_update'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    
    # Evaluation URLs
    path('evaluations/', views.evaluation_list, name='evaluation_list'),
    path('evaluations/create/', views.evaluation_create, name='evaluation_create'),
    path('evaluations/<int:pk>/update/', views.evaluation_update, name='evaluation_update'),
    path('evaluations/<int:pk>/delete/', views.evaluation_delete, name='evaluation_delete'),
    path('evaluations/<int:pk>/download-pdf/', views.evaluation_download_pdf, name='evaluation_download_pdf'),
    path('api/training/<int:train_id>/participants/', views.get_training_participants, name='get_training_participants'),
    path('api/training/<int:train_id>/available-participants/', views.get_available_participants, name='get_available_participants'),
    
    # Professor URLs
    path('professors/', views.professor_list, name='professor_list'),
    path('professors/create/', views.professor_create, name='professor_create'),
    path('professors/<int:pk>/update/', views.professor_update, name='professor_update'),
    path('professors/<int:pk>/delete/', views.professor_delete, name='professor_delete'),
    path('professors/<int:pk>/download-pdf/', views.professor_download_pdf, name='professor_download_pdf'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/update/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Participant URLs
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/update/', views.participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),
    
    # Location URLs
    path('locations/', views.location_list, name='location_list'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<int:pk>/update/', views.location_update, name='location_update'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),
    
    # Training Session URLs
    path('training/', views.train_list, name='train_list'),
    path('training/create/', views.train_create, name='train_create'),
    path('training/<int:pk>/update/', views.train_update, name='train_update'),
    path('training/<int:pk>/delete/', views.train_delete, name='train_delete'),
    path('training/<int:pk>/download-evaluations-pdf/', views.train_download_evaluations_pdf, name='train_download_evaluations_pdf'),
    
    # Training Participant URLs
    path('training-participants/', views.train_participant_list, name='train_participant_list'),
    path('training-participants/create/', views.train_participant_create, name='train_participant_create'),
    path('training-participants/<int:pk>/update/', views.train_participant_update, name='train_participant_update'),
    path('training-participants/<int:pk>/delete/', views.train_participant_delete, name='train_participant_delete'),
    
    # System Management URLs
    path('system-closed/', views.system_closed, name='system_closed'),
    path('toggle-system-status/', views.toggle_system_status, name='toggle_system_status'),
    path('system-settings/', views.manage_system_settings, name='manage_system_settings'),
    
    # Database Backup URLs (Admin Only)
    path('database-backup/', views.database_backup, name='database_backup'),
    path('database-backup/create/', views.database_backup_create, name='database_backup_create'),
    path('database-backup/restore/<str:filename>/', views.database_backup_restore, name='database_backup_restore'),
    path('database-backup/download/<str:filename>/', views.database_backup_download, name='database_backup_download'),
    path('database-backup/delete/<str:filename>/', views.database_backup_delete, name='database_backup_delete'),
    
    # AI Assistant URLs
    path('ai/chatbot/', ai_views.ai_chatbot, name='ai_chatbot'),
    path('ai/professor/<int:pk>/report/', ai_views.ai_professor_report, name='ai_professor_report'),
    path('ai/dashboard/insights/', ai_views.ai_dashboard_insights, name='ai_dashboard_insights'),
    path('ai/analyze-notes/', ai_views.ai_analyze_notes, name='ai_analyze_notes'),
    path('ai/contact/<int:pk>/categorize/', ai_views.ai_categorize_contact, name='ai_categorize_contact'),
    path('ai/status/', ai_views.ai_status, name='ai_status'),
]
