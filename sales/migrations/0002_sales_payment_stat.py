# Generated by Django 5.1.2 on 2024-12-02 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='payment_stat',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Online', 'Online'), ('Terms', 'Terms')], default='Pending', max_length=50),
        ),
    ]