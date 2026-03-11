from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_app', '0003_update_participant_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE Participant_tbl (
                Participant_ID BIGINT NOT NULL PRIMARY KEY,
                Participant_name NVARCHAR(35) NOT NULL,
                Participant_phone BIGINT NULL,
                Participant_Email NVARCHAR(50) NULL
            )
            """,
            reverse_sql="DROP TABLE Participant_tbl"
        ),
    ]
