# Generated by Django 4.0.4 on 2022-06-02 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_products_selling_price_orderitems_imei_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='selling_price',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]