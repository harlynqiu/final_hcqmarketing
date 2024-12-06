# Generated by Django 5.1.1 on 2024-12-06 04:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_serializedinventory'),
        ('products', '0006_product_datestart'),
        ('purchases', '0005_purchaseitem_serial_numbers_purchasereturn_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='customer_hardware',
        ),
        migrations.AlterField(
            model_name='inventory',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='purchase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchases.purchase'),
        ),
    ]