# Generated by Django 3.2.12 on 2022-08-21 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0037_auto_20220821_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='productstockin',
            name='asset',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
