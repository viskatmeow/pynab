# Generated by Django 2.2.6 on 2019-12-11 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nabairqualityd', '0002_auto_20191204_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='airquality',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='localisation',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='next_performance_type',
            field=models.TextField(null=True),
        ),
    ]
