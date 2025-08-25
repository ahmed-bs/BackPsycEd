# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ProfileItem', '0002_add_arabic_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profileitem',
            old_name='comentaire',
            new_name='commentaire',
        ),
    ]
