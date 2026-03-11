from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    ContactMessage, EvaluationTab, ProfessorTbl, CourseTbl, ParticipantTbl, 
    LocationTbl, UserProfile, SystemSettings, TrainTbl, TrainParticipantTbl
)


# UserProfile Inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['role', 'phone', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


# Extend User Admin
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'profile__role']
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'N/A'
    get_role.short_description = 'Role'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at', 'subject']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    actions = [mark_as_read, mark_as_unread]


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['is_system_open', 'closure_start_date', 'closure_end_date', 'allow_admin_access', 'last_updated', 'updated_by']
    fieldsets = [
        ('System Status', {
            'fields': ['is_system_open', 'allow_admin_access']
        }),
        ('Closure Information', {
            'fields': ['closure_message', 'closure_start_date', 'closure_end_date']
        }),
        ('Last Update', {
            'fields': ['last_updated', 'updated_by'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['last_updated', 'closure_start_date']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False


# Register new models
@admin.register(TrainTbl)
class TrainTblAdmin(admin.ModelAdmin):
    list_display = ['trainid', 'get_course_name', 'get_professor_name', 'get_location_name', 'train_date', 'is_active']
    list_filter = ['is_active', 'train_date', 'course', 'professor', 'location']
    search_fields = ['trainid', 'course__coursename', 'professor__profname', 'location__locationname']
    date_hierarchy = 'train_date'
    ordering = ['-train_date', '-trainid']
    
    def get_course_name(self, obj):
        return obj.course.coursename if obj.course else 'N/A'
    get_course_name.short_description = 'Course'
    get_course_name.admin_order_field = 'course__coursename'
    
    def get_professor_name(self, obj):
        return obj.professor.profname if obj.professor else 'N/A'
    get_professor_name.short_description = 'Professor'
    get_professor_name.admin_order_field = 'professor__profname'
    
    def get_location_name(self, obj):
        return obj.location.locationname if obj.location else 'N/A'
    get_location_name.short_description = 'Location'
    get_location_name.admin_order_field = 'location__locationname'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('course', 'professor', 'location')


@admin.register(TrainParticipantTbl)
class TrainParticipantTblAdmin(admin.ModelAdmin):
    list_display = ['train_participant_id', 'get_train_info', 'get_participant_name', 'evaluation_date', 'is_active']
    list_filter = ['is_active', 'evaluation_date', 'train']
    search_fields = ['train__trainid', 'participant__participant_name']
    date_hierarchy = 'evaluation_date'
    ordering = ['-evaluation_date', '-train_participant_id']
    
    def get_train_info(self, obj):
        if obj.train and obj.train.course:
            return f"Train #{obj.train.trainid}: {obj.train.course.coursename}"
        return f"Train #{obj.train.trainid}" if obj.train else 'N/A'
    get_train_info.short_description = 'Training Session'
    get_train_info.admin_order_field = 'train__trainid'
    
    def get_participant_name(self, obj):
        return obj.participant.participant_name if obj.participant else 'N/A'
    get_participant_name.short_description = 'Participant'
    get_participant_name.admin_order_field = 'participant__participant_name'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('train', 'train__course', 'participant')
