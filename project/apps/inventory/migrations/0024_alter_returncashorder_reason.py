# Generated by Django 3.2.12 on 2022-08-11 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_remove_cashorder_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returncashorder',
            name='reason',
            field=models.CharField(choices=[('NOT_INTERESTED', 'Not Interested'), ('ISSUE', 'Issue'), ('CUSTOM', 'Custom')], max_length=20),
        ),
    ]
