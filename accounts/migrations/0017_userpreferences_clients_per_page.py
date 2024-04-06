# Generated by Django 4.2.7 on 2024-04-06 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_alter_company_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreferences',
            name='clients_per_page',
            field=models.IntegerField(choices=[(10, '10 (Default)'), (20, '20'), (30, '30'), (-1, 'Show All')], default=10),
        ),
    ]
