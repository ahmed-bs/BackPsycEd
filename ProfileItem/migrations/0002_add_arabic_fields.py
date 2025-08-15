# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProfileItem', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileitem',
            name='name_ar',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='profileitem',
            name='description_ar',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profileitem',
            name='commentaire_ar',
            field=models.TextField(blank=True, null=True),
        ),
    ] 