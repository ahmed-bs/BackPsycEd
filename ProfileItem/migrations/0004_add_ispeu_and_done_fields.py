# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProfileItem', '0003_rename_comentaire_to_commentaire'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileitem',
            name='isPeu',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profileitem',
            name='done',
            field=models.BooleanField(default=False),
        ),
    ]

