# Generated by Django 5.1.6 on 2025-02-17 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0007_historicalclient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='status',
        ),
        migrations.RemoveField(
            model_name='historicalclient',
            name='status',
        ),
    ]
