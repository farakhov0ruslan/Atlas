# Generated by Django 5.1.3 on 2025-05-20 00:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_subscriptionplan_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='main.subscriptionplan', verbose_name='Тарифный план'),
        ),
    ]
