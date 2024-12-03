# Generated by Django 5.1.1 on 2024-12-03 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_alter_sales_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
