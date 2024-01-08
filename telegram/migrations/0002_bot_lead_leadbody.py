# Generated by Django 4.2.8 on 2024-01-06 01:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('telegram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('token', models.CharField(max_length=100)),
                ('token_canal', models.CharField(max_length=100)),
                ('criado', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bot',
                'verbose_name_plural': 'Bots',
                'ordering': ['-criado'],
            },
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('bot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram.bot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Lead',
                'verbose_name_plural': 'Leads',
            },
        ),
        migrations.CreateModel(
            name='LeadBody',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horario', models.CharField(max_length=100)),
                ('criado', models.DateTimeField(auto_now_add=True)),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram.lead')),
                ('mensagens', models.ManyToManyField(to='telegram.mensagem')),
            ],
            options={
                'verbose_name': 'Lead Group',
                'verbose_name_plural': 'Lead Groups',
                'ordering': ['-criado'],
            },
        ),
    ]
