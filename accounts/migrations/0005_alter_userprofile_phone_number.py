# Generated by Django 4.2.7 on 2023-12-14 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_customuser_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
