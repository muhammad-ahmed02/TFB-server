# Generated by Django 3.2.12 on 2022-08-08 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_cashorder_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashorder',
            name='quantity',
        ),
    ]