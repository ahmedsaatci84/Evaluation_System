from django.db import models
from .participant import ParticipantTbl
from .training import TrainTbl


class EvaluationTab(models.Model):
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
    participant = models.ForeignKey(
        ParticipantTbl,
        on_delete=models.CASCADE,
        db_column='ParticipantID',
        blank=True,
        null=True,
        related_name='evaluations',
    )
    train = models.ForeignKey(
        TrainTbl,
        on_delete=models.CASCADE,
        db_column='TrainID',
        blank=True,
        null=True,
        related_name='evaluations',
    )

    class Meta:
        managed = False
        db_table = 'Evaluation_TAB'
        verbose_name = 'Evaluation'
        verbose_name_plural = 'Evaluations'
        constraints = [
            models.UniqueConstraint(
                fields=['participant', 'train'],
                name='unique_participant_train_evaluation',
                violation_error_message=(
                    'An evaluation from this participant for this training session already exists.'
                ),
            )
        ]

    def __str__(self):
        train_info = f"Train #{self.train.trainid}" if self.train else "No Training"
        return f"Evaluation #{self.id} - {train_info}"

    def get_q_average(self):
        q_fields = [
            self.ev_q_1, self.ev_q_2, self.ev_q_3, self.ev_q_4, self.ev_q_5,
            self.ev_q_6, self.ev_q_7, self.ev_q_8, self.ev_q_9, self.ev_q_10,
            self.ev_q_11, self.ev_q_12, self.ev_q_13, self.ev_q_14, self.ev_q_15,
        ]
        valid_values = [v for v in q_fields if v is not None]
        if valid_values:
            return sum(valid_values) / len(valid_values)
        return None

    def get_course(self):
        return self.train.course if self.train else None

    def get_professor(self):
        return self.train.professor if self.train else None

    def get_location(self):
        return self.train.location if self.train else None
