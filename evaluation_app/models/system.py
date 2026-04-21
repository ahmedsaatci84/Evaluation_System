from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    USER_ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('guest', 'Guest'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='guest')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin'

    def is_user(self):
        return self.role == 'user'

    def is_guest(self):
        return self.role == 'guest'

    def can_create(self):
        return self.role in ['admin', 'user']

    def can_edit(self):
        return self.role in ['admin', 'user']

    def can_delete(self):
        return self.role == 'admin'

    def can_view_contacts(self):
        return self.role in ['admin', 'user']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class SystemSettings(models.Model):
    is_system_open = models.BooleanField(
        default=True,
        verbose_name='System Open',
        help_text='When unchecked, the system will be closed for maintenance',
    )
    closure_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Closure Message',
        help_text='Message to display when system is closed',
        default='The system is currently closed for maintenance. Please check back later.',
    )
    closure_start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Closure Start Date',
        help_text='When the system closure started',
    )
    closure_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expected Closure End Date',
        help_text='Expected date when system will reopen',
    )
    allow_admin_access = models.BooleanField(
        default=True,
        verbose_name='Allow Admin Access',
        help_text='Allow admin users to access the system when closed',
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings_updates',
    )

    class Meta:
        managed = True
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        status = "Open" if self.is_system_open else "Closed"
        return f"System Status: {status}"

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
