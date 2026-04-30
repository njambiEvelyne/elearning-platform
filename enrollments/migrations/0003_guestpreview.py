# Generated migration for GuestPreview model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0002_alter_enrollment_course'),
        ('courses', '0005_alter_lesson_options_lesson_duration_minutes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuestPreview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_email', models.EmailField(max_length=254)),
                ('guest_session_id', models.CharField(max_length=255, unique=True)),
                ('preview_started_at', models.DateTimeField(auto_now_add=True)),
                ('last_accessed_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_previews', to='courses.course')),
            ],
            options={
                'verbose_name': 'Guest Preview',
                'verbose_name_plural': 'Guest Previews',
            },
        ),
        migrations.AlterUniqueTogether(
            name='guestpreview',
            unique_together={('course', 'guest_session_id')},
        ),
    ]
