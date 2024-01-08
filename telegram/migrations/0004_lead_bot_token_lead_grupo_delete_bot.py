# Generated by Django 4.2.8 on 2024-01-08 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0003_remove_lead_bot'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='bot_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='grupo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Bot',
        ),
    ]