# Generated by Django 5.1.1 on 2024-12-06 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_alter_salesreturn_return_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='walk_in_customer_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
