# Generated by Django 5.1.1 on 2024-11-28 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_remove_customer_customer_hardware_customer_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_hardware',
            field=models.CharField(default='Unknown', max_length=100),
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.DeleteModel(
            name='CustomerHardware',
        ),
    ]