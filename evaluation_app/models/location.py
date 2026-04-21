from django.db import models


class LocationTbl(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    locationname = models.CharField(db_column='LocationName', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Location_tbl'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.locationname or f"Location ID: {self.id}"
