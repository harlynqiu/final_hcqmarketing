# Generated by Django 5.1.1 on 2024-12-05 01:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0010_invoice_sales_sales_invoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='sale',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='sales.sales'),
        ),
    ]
