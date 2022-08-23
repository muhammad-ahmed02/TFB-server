# Generated by Django 3.2.12 on 2022-08-22 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0039_claim_credit_credititem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credit',
            name='product_stock',
        ),
        migrations.AddField(
            model_name='credit',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]