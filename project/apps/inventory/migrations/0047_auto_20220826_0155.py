# Generated by Django 3.2.12 on 2022-08-26 01:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0046_auto_20220826_0118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claim',
            name='product',
        ),
        migrations.RemoveField(
            model_name='claim',
            name='vendor',
        ),
        migrations.AlterField(
            model_name='claim',
            name='product_stock',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.productstockin'),
            preserve_default=False,
        ),
    ]
