# Generated migration for adding unique constraint to Professor model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_app', '0005_contactmessage'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='professortbl',
            constraint=models.UniqueConstraint(
                fields=['profname', 'prophone'],
                name='unique_professor_name_phone'
            ),
        ),
    ]
