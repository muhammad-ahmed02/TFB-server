# Generated by Django 3.2.12 on 2022-08-04 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_setting_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashorder',
            name='sale_price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='products',
            name='purchasing_price',
            field=models.IntegerField(),
        ),
    ]
