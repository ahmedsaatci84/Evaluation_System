from django.db import models


class ParticipantTbl(models.Model):
    participant_id = models.BigIntegerField(db_column='Participant_ID', primary_key=True)
    participant_name = models.CharField(db_column='Participant_name', max_length=35)
    participant_phone = models.BigIntegerField(db_column='Participant_phone', blank=True, null=True)
    participant_email = models.CharField(db_column='Participant_Email', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Participant_tbl'
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'

    def __str__(self):
        return self.participant_name
