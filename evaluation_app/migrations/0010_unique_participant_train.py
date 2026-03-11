# Generated migration for adding unique constraint to prevent duplicate evaluations
# from the same participant on the same training session

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_app', '0009_add_train_models'),
    ]

    operations = [
        # Add unique constraint to prevent duplicate evaluations
        # Note: Since managed=False, this migration documents the constraint
        # but does not create it in the database automatically.
        # Run the following SQL in your database to create the constraint:
        # 
        # ALTER TABLE Evaluation_TAB
        # ADD CONSTRAINT unique_participant_train_evaluation 
        # UNIQUE (ParticipantID, TrainID);
        
        migrations.AddConstraint(
            model_name='evaluationtab',
            constraint=models.UniqueConstraint(
                fields=['participant', 'train'],
                name='unique_participant_train_evaluation',
                violation_error_message='An evaluation from this participant for this training session already exists.'
            ),
        ),
    ]
