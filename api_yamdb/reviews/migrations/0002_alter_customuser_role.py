# Generated by Django 3.2 on 2023-02-28 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(blank=True, choices=[('admin', 'Администратор'), ('moderator', 'Модератор'), ('user', 'Пользователь')], default='user', max_length=9),
        ),
    ]
