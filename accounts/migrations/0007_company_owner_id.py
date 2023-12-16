# Generated by Django 4.2.7 on 2023-12-16 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_company_address_lines_alter_company_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='owner_id',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owner', to='accounts.owner'),
        ),
    ]
