# Generated migration for adding Train and TrainParticipant models
# and modifying Evaluation model to match SQL schema

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_app', '0008_systemsettings'),
    ]

    operations = [
        # Note: Since managed=False, these operations are for documentation only
        # The actual tables already exist in the database
        
        # Create TrainTbl model (managed=False, table exists in DB)
        migrations.CreateModel(
            name='TrainTbl',
            fields=[
                ('trainid', models.BigAutoField(db_column='TrainID', primary_key=True, serialize=False)),
                ('train_date', models.DateField(blank=True, db_column='Train_Date', null=True)),
                ('is_active', models.BooleanField(blank=True, db_column='IS_Active', default=True, null=True)),
                ('course', models.ForeignKey(blank=True, db_column='CourseID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_sessions', to='evaluation_app.coursetbl')),
                ('location', models.ForeignKey(blank=True, db_column='LocationID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_sessions', to='evaluation_app.locationtbl')),
                ('professor', models.ForeignKey(blank=True, db_column='ProfessorID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_sessions', to='evaluation_app.professortbl')),
            ],
            options={
                'verbose_name': 'Training Session',
                'verbose_name_plural': 'Training Sessions',
                'db_table': 'Train_tbl',
                'managed': False,
            },
        ),
        
        # Create TrainParticipantTbl model (managed=False, table exists in DB)
        migrations.CreateModel(
            name='TrainParticipantTbl',
            fields=[
                ('train_participant_id', models.BigAutoField(db_column='Train_Paticipant_id', primary_key=True, serialize=False)),
                ('evaluation_date', models.DateField(blank=True, db_column='Evaluation_Date', null=True)),
                ('is_active', models.BooleanField(blank=True, db_column='IS_Active', default=True, null=True)),
                ('participant', models.ForeignKey(blank=True, db_column='ParticipantID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_sessions', to='evaluation_app.participanttbl')),
                ('train', models.ForeignKey(db_column='TrainID', on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='evaluation_app.traintbl')),
            ],
            options={
                'verbose_name': 'Training Participant',
                'verbose_name_plural': 'Training Participants',
                'db_table': 'Train_Participant_tbl',
                'managed': False,
            },
        ),
    ]
