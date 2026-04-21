from django.db import models


class ProfessorTbl(models.Model):
    profid = models.BigIntegerField(db_column='ProfID', primary_key=True)
    profname = models.CharField(db_column='ProFName', max_length=50, blank=True, null=True)
    prophone = models.BigIntegerField(db_column='ProPhone', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Professor_tbl'
        verbose_name = 'Professor'
        verbose_name_plural = 'Professors'
        constraints = [
            models.UniqueConstraint(
                fields=['profid', 'profname', 'prophone'],
                name='unique_professor_name_phone'
            ),
        ]

    def __str__(self):
        return self.profname or f"Professor ID: {self.profid}"
