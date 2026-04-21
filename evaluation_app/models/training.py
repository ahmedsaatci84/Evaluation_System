from django.db import models
from .course import CourseTbl
from .professor import ProfessorTbl
from .location import LocationTbl
from .participant import ParticipantTbl


class TrainTbl(models.Model):
    trainid = models.BigAutoField(db_column='TrainID', primary_key=True)
    train_date = models.DateField(db_column='Train_Date', blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_Active', blank=True, null=True, default=True)
    course = models.ForeignKey(
        CourseTbl,
        on_delete=models.CASCADE,
        db_column='CourseID',
        blank=True,
        null=True,
        related_name='training_sessions',
    )
    professor = models.ForeignKey(
        ProfessorTbl,
        on_delete=models.CASCADE,
        db_column='ProfessorID',
        blank=True,
        null=True,
        related_name='training_sessions',
    )
    location = models.ForeignKey(
        LocationTbl,
        on_delete=models.CASCADE,
        db_column='LocationID',
        blank=True,
        null=True,
        related_name='training_sessions',
    )

    class Meta:
        managed = False
        db_table = 'Train_tbl'
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'

    def __str__(self):
        course_name = self.course.coursename if self.course else "No Course"
        return f"Train #{self.trainid}: {course_name} on {self.train_date}"


class TrainParticipantTbl(models.Model):
    train_participant_id = models.BigAutoField(db_column='Train_Paticipant_id', primary_key=True)
    evaluation_date = models.DateField(db_column='Evaluation_Date', blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_Active', blank=True, null=True, default=True)
    train = models.ForeignKey(
        TrainTbl,
        on_delete=models.CASCADE,
        db_column='TrainID',
        related_name='participants',
    )
    participant = models.ForeignKey(
        ParticipantTbl,
        on_delete=models.CASCADE,
        db_column='ParticipantID',
        blank=True,
        null=True,
        related_name='training_sessions',
    )

    class Meta:
        managed = False
        db_table = 'Train_Participant_tbl'
        verbose_name = 'Training Participant'
        verbose_name_plural = 'Training Participants'

    def __str__(self):
        participant_name = self.participant.participant_name if self.participant else "Unknown"
        return f"{participant_name} in Train #{self.train.trainid}"
