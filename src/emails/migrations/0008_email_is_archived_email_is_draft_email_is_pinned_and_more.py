# Generated by Django 5.2.4 on 2025-07-28 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0007_email_direction'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='email',
            name='is_draft',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='email',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='email',
            name='is_replied',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='email',
            name='is_snoozed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='email',
            name='snoozed_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
