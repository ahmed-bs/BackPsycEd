# Generated manually to add Arabic fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='title_ar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='goal',
            name='description_ar',
            field=models.TextField(blank=True, null=True),
        ),
    ] 