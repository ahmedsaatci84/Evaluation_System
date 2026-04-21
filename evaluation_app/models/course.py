from django.db import models
from .professor import ProfessorTbl


class CourseTbl(models.Model):
    cid = models.BigAutoField(db_column='cid', primary_key=True)
    courseid = models.CharField(db_column='CourseID', max_length=50, blank=True, null=True)
    coursename = models.CharField(db_column='CourseName', max_length=50, blank=True, null=True)
    prof = models.ForeignKey(
        ProfessorTbl,
        models.DO_NOTHING,
        db_column='ProfID',
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = 'Course_tbl'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.coursename or f"Course ID: {self.cid}"
