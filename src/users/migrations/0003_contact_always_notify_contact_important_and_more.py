# Generated by Django 5.2.4 on 2025-07-26 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_userprofile_supabase_user_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='always_notify',
            field=models.BooleanField(default=False, help_text='Always notify user for emails from this contact'),
        ),
        migrations.AddField(
            model_name='contact',
            name='important',
            field=models.BooleanField(default=False, help_text='Mark this contact as important (priority)'),
        ),
        migrations.AddField(
            model_name='contact',
            name='marked_as_spam',
            field=models.BooleanField(default=False, help_text='Automatically mark emails from this contact as spam'),
        ),
        migrations.AddField(
            model_name='contact',
            name='muted',
            field=models.BooleanField(default=False, help_text='Mute all emails from this contact'),
        ),
        migrations.AddField(
            model_name='contact',
            name='whitelist',
            field=models.BooleanField(default=False, help_text='Bypass spam filters for this contact'),
        ),
    ]
