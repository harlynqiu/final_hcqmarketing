# Generated by Django 5.1.1 on 2024-12-03 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_alter_salesitem_price_per_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesitem',
            name='price_per_item',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]