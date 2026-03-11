from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Using managed=False because the tables already exist in the MSSQL database
# and we don't want Django to manage their creation/deletion.

class ProfessorTbl(models.Model):
    # Primary key is not auto-incrementing in SQL script, so we define it explicitly
    profid = models.BigIntegerField(db_column='ProfID', primary_key=True)
    profname = models.CharField(db_column='ProFName', max_length=50, blank=True, null=True)
    # numeric(18, 0) is mapped to BigIntegerField for simplicity
    prophone = models.BigIntegerField(db_column='ProPhone', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Professor_tbl'
        verbose_name = 'Professor'
        verbose_name_plural = 'Professors'
        # Prevent duplicate professors based on name and phone combination
        constraints = [
            models.UniqueConstraint(
                fields=['profid','profname', 'prophone'],
                name='unique_professor_name_phone'
            ),
        ]

    def __str__(self):
        return self.profname or f"Professor ID: {self.profid}"

class ParticipantTbl(models.Model):
    participant_id = models.BigIntegerField(db_column='Participant_ID', primary_key=True)
    participant_name = models.CharField(db_column='Participant_name', max_length=35)
    participant_phone = models.BigIntegerField(db_column='Participant_phone', blank=True, null=True)
    participant_email = models.CharField(db_column='Participant_Email', max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Participant_tbl'
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'

    def __str__(self):
        return self.participant_name

class LocationTbl(models.Model):
    # id is auto-incrementing (IDENTITY(1,1))
    id = models.BigAutoField(db_column='id', primary_key=True)
    locationname = models.CharField(db_column='LocationName', max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Location_tbl'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.locationname or f"Location ID: {self.id}"

class CourseTbl(models.Model):
    """Course information"""
    # cid is auto-incrementing (IDENTITY(1,1))
    cid = models.BigAutoField(db_column='cid', primary_key=True)
    courseid = models.CharField(db_column='CourseID', max_length=50, blank=True, null=True)
    coursename = models.CharField(db_column='CourseName', max_length=50, blank=True, null=True)
    # Foreign Key to ProfessorTbl
    prof = models.ForeignKey(ProfessorTbl, models.CASCADE, db_column='ProfID', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Course_tbl'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.coursename or f"Course ID: {self.cid}"


class TrainTbl(models.Model):
    """Training session model linking Course, Professor, and Location"""
    # Primary key is auto-incrementing (IDENTITY(1,1))
    trainid = models.BigAutoField(db_column='TrainID', primary_key=True)
    train_date = models.DateField(db_column='Train_Date', blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_Active', blank=True, null=True, default=True)

    # Foreign Keys
    course = models.ForeignKey(
        CourseTbl, 
        on_delete=models.CASCADE, 
        db_column='CourseID', 
        blank=True, 
        null=True,
        related_name='training_sessions'
    )
    professor = models.ForeignKey(
        ProfessorTbl, 
        on_delete=models.CASCADE, 
        db_column='ProfessorID', 
        blank=True, 
        null=True,
        related_name='training_sessions'
    )
    location = models.ForeignKey(
        LocationTbl, 
        on_delete=models.CASCADE, 
        db_column='LocationID', 
        blank=True, 
        null=True,
        related_name='training_sessions'
    )

    class Meta:
        managed = True
        db_table = 'Train_tbl'
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'

    def __str__(self):
        course_name = self.course.coursename if self.course else "No Course"
        return f"Train #{self.trainid}: {course_name} on {self.train_date}"


class TrainParticipantTbl(models.Model):
    """Junction table linking Training sessions with Participants"""
    # Primary key is auto-incrementing (IDENTITY(1,1))
    train_participant_id = models.BigAutoField(db_column='Train_Paticipant_id', primary_key=True)
    evaluation_date = models.DateField(db_column='Evaluation_Date', blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_Active', blank=True, null=True, default=True)

    # Foreign Keys
    train = models.ForeignKey(
        TrainTbl,
        on_delete=models.CASCADE,
        db_column='TrainID',
        blank=True,
        null=True,
        related_name='participants'
    )
    participant = models.ForeignKey(
        ParticipantTbl,
        on_delete=models.CASCADE,
        db_column='ParticipantID',
        blank=True,
        null=True,
        related_name='training_sessions'
    )

    class Meta:
        managed = True
        db_table = 'Train_Participant_tbl'
        verbose_name = 'Training Participant'
        verbose_name_plural = 'Training Participants'

    def __str__(self):
        participant_name = self.participant.participant_name if self.participant else "Unknown"
        return f"{participant_name} in Train #{self.train.trainid}"


class EvaluationTab(models.Model):
    """Evaluation form responses linked to Training sessions and Participants"""
    # id is auto-incrementing (IDENTITY(1,1))
    id = models.BigAutoField(db_column='id', primary_key=True)
    ev_q_1 = models.IntegerField(db_column='Ev_Q_1', blank=True, null=True)
    ev_q_2 = models.IntegerField(db_column='Ev_Q_2', blank=True, null=True)
    ev_q_3 = models.IntegerField(db_column='Ev_Q_3', blank=True, null=True)
    ev_q_4 = models.IntegerField(db_column='Ev_Q_4', blank=True, null=True)
    ev_q_5 = models.IntegerField(db_column='Ev_Q_5', blank=True, null=True)
    ev_q_6 = models.IntegerField(db_column='Ev_Q_6', blank=True, null=True)
    ev_q_7 = models.IntegerField(db_column='Ev_Q_7', blank=True, null=True)
    ev_q_8 = models.IntegerField(db_column='Ev_Q_8', blank=True, null=True)
    ev_q_9 = models.IntegerField(db_column='Ev_Q_9', blank=True, null=True)
    ev_q_10 = models.IntegerField(db_column='Ev_Q_10', blank=True, null=True)
    ev_q_11 = models.IntegerField(db_column='Ev_Q_11', blank=True, null=True)
    ev_q_12 = models.IntegerField(db_column='Ev_Q_12', blank=True, null=True)
    ev_q_13 = models.IntegerField(db_column='Ev_Q_13', blank=True, null=True)
    ev_q_14 = models.IntegerField(db_column='Ev_Q_14', blank=True, null=True)
    ev_q_15 = models.IntegerField(db_column='Ev_Q_15', blank=True, null=True)
    ev_q_notes = models.TextField(db_column='Ev_Q_Notes', blank=True, null=True)

    # Foreign Keys - matching SQL schema
    participant = models.ForeignKey(
        ParticipantTbl, 
        on_delete=models.CASCADE, 
        db_column='ParticipantID', 
        blank=True, 
        null=True,
        related_name='evaluations'
    )
    train = models.ForeignKey(
        TrainTbl,
        on_delete=models.CASCADE,
        db_column='TrainID',
        blank=True,
        null=True,
        related_name='evaluations'
    )

    class Meta:
        managed = True
        db_table = 'Evaluation_TAB'
        verbose_name = 'Evaluation'
        verbose_name_plural = 'Evaluations'
        # Unique constraint to prevent duplicate evaluations
        # Note: Since managed=False, this constraint must be created in the database manually
        constraints = [
            models.UniqueConstraint(
                fields=['participant', 'train'],
                name='unique_participant_train_evaluation',
                violation_error_message='An evaluation from this participant for this training session already exists.'
            )
        ]
    
    def __str__(self):
        train_info = f"Train #{self.train.trainid}" if self.train else "No Training"
        return f"Evaluation #{self.id} - {train_info}"
    
    def get_q_average(self):
        """Calculate the average of all Q1-Q15 fields."""
        q_fields = [
            self.ev_q_1, self.ev_q_2, self.ev_q_3, self.ev_q_4, self.ev_q_5,
            self.ev_q_6, self.ev_q_7, self.ev_q_8, self.ev_q_9, self.ev_q_10,
            self.ev_q_11, self.ev_q_12, self.ev_q_13, self.ev_q_14, self.ev_q_15
        ]
        valid_values = [v for v in q_fields if v is not None]
        if valid_values:
            return sum(valid_values) / len(valid_values)
        return None
    
    def get_course(self):
        """Get the course through the training session"""
        return self.train.course if self.train else None
    
    def get_professor(self):
        """Get the professor through the training session"""
        return self.train.professor if self.train else None
    
    def get_location(self):
        """Get the location through the training session"""
        return self.train.location if self.train else None

class ContactMessage(models.Model):
    """Model to store contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        managed = True
        db_table = 'contact_messages'
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def mark_as_unread(self):
        """Mark this message as unread"""
        self.is_read = False
        self.save(update_fields=['is_read'])
    
    def get_status_display(self):
        """Return a human-readable status"""
        return "Read" if self.is_read else "Unread"
    
    @classmethod
    def get_unread_count(cls):
        """Get count of unread messages"""
        return cls.objects.filter(is_read=False).count()
    
    @classmethod
    def get_recent_messages(cls, limit=5):
        """Get recent contact messages"""
        return cls.objects.all()[:limit]


class UserProfile(models.Model):
    """Extended user profile with role-based authentication"""
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
        """Check if user can create records"""
        return self.role in ['admin', 'user']
    
    def can_edit(self):
        """Check if user can edit records"""
        return self.role in ['admin', 'user']
    
    def can_delete(self):
        """Check if user can delete records"""
        return self.role == 'admin'
    
    def can_view_contacts(self):
        """Check if user can view contact messages"""
        return self.role in ['admin', 'user']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


# Removed save_user_profile signal to prevent recursion issues
# Profile should be saved explicitly when needed


class SystemSettings(models.Model):
    """System-wide settings including system open/close status"""
    is_system_open = models.BooleanField(
        default=True,
        verbose_name='System Open',
        help_text='When unchecked, the system will be closed for maintenance'
    )
    closure_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Closure Message',
        help_text='Message to display when system is closed',
        default='The system is currently closed for maintenance. Please check back later.'
    )
    closure_start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Closure Start Date',
        help_text='When the system closure started'
    )
    closure_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expected Closure End Date',
        help_text='Expected date when system will reopen'
    )
    allow_admin_access = models.BooleanField(
        default=True,
        verbose_name='Allow Admin Access',
        help_text='Allow admin users to access the system when closed'
    )
    allow_guest_evaluations = models.BooleanField(
        default=True,
        verbose_name='Allow Guest Evaluations',
        help_text='Allow guest users to create evaluations'
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings_updates'
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
        """Get or create system settings singleton"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of settings"""
        pass
    
    @classmethod
    def load(cls):
        """Load settings, create if doesn't exist"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
