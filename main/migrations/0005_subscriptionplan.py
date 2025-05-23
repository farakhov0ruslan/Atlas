# Generated by Django 5.1.3 on 2025-05-19 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_subscription_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Уникальный код плана (e.g. ‘weekend’, ‘vacation’)', max_length=50, unique=True)),
                ('name', models.CharField(help_text='Человеко-читаемое название (Пакет «Выходные»)', max_length=100)),
                ('routes', models.PositiveIntegerField(help_text='Сколько маршрутов даёт план')),
                ('duration', models.DurationField(help_text='Длительность подписки (например, 30 дней)')),
                ('price', models.DecimalField(decimal_places=2, help_text='Цена в рублях', max_digits=8)),
                ('currency', models.CharField(default='RUB', max_length=3)),
            ],
            options={
                'verbose_name': 'Тарифный план',
                'verbose_name_plural': 'Тарифные планы',
            },
        ),
    ]
