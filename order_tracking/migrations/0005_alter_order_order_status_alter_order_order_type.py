# Generated by Django 4.2.7 on 2024-03-17 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_tracking', '0004_order_estimated_cost_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('purchase', 'Purchase'), ('repair', 'Repair'), ('other', 'Other')], default='in_progress'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='purhcase'),
        ),
    ]
