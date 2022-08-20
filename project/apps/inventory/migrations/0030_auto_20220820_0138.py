# Generated by Django 3.2.12 on 2022-08-20 01:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0029_rename_imei_number_cashorder_imei_or_serial_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductStockIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchasing_price', models.IntegerField()),
                ('available_stock', models.PositiveIntegerField(default=0)),
                ('sold', models.PositiveIntegerField(default=0)),
                ('on_credit', models.PositiveIntegerField(default=0)),
                ('on_claim', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('imei_or_serial_number', models.ManyToManyField(blank=True, to='inventory.IMEINumber')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='orderitems',
            name='order',
        ),
        migrations.RemoveField(
            model_name='orderitems',
            name='product',
        ),
        migrations.RemoveField(
            model_name='products',
            name='imei_or_serial_number',
        ),
        migrations.RemoveField(
            model_name='cashorder',
            name='product',
        ),
        migrations.AddField(
            model_name='cashorder',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='cashorder',
            name='total_amount',
            field=models.IntegerField(blank=True, help_text='Calculated Automatically', null=True),
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='OrderItems',
        ),
        migrations.DeleteModel(
            name='products',
        ),
        migrations.AddField(
            model_name='productstockin',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.vendor'),
        ),
        migrations.AddField(
            model_name='cashorder',
            name='product_stock',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.productstockin'),
            preserve_default=False,
        ),
    ]