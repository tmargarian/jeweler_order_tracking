# Generated by Django 4.2.7 on 2024-04-06 05:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order_tracking', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='total_spent',
        ),
    ]
