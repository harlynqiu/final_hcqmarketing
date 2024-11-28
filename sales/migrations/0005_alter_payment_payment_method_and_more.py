# Generated by Django 5.1.1 on 2024-11-28 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_customer_remove_saleitem_sale_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Card', 'Card'), ('Bank Transfer', 'Bank Transfer'), ('Gcash', 'Gcash')], default='Cash', max_length=50),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Bank Transfer', 'Bank Transfer'), ('Gcash', 'Gcash')], default='Completed', max_length=50),
        ),
        migrations.AlterField(
            model_name='sales',
            name='payment_status',
            field=models.CharField(choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid'), ('Partial', 'Partial')], default='Unpaid', max_length=50),
        ),
    ]