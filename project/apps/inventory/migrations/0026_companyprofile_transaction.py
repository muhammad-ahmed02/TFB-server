# Generated by Django 3.2.12 on 2022-08-16 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_auto_20220815_1110'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(max_length=54)),
                ('owner_balance', models.IntegerField(default=0)),
                ('business_balance', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_profit', models.IntegerField()),
                ('seller_profit', models.IntegerField()),
                ('owner_profit', models.IntegerField()),
                ('business_profit', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.companyprofile')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.cashorder')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.sellerprofile')),
            ],
        ),
    ]
