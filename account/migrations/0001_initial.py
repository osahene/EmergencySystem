# Generated by Django 4.2.16 on 2024-12-04 21:53

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True, validators=[django.core.validators.EmailValidator()], verbose_name='email address')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('is_phone_verified', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('abstractuserprofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('subscription_level', models.CharField(choices=[('free', 'Free'), ('pro', 'Pro'), ('advance', 'Advance')], default='free', max_length=20)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'indexes': [models.Index(fields=['first_name', 'last_name'], name='account_use_first_n_0ce1b3_idx')],
            },
            bases=('account.abstractuserprofile',),
        ),
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_code', models.CharField(max_length=255)),
                ('expiration_time', models.DateTimeField()),
                ('failed_attempts', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otps', to='account.users')),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('abstractuserprofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('institution_name', models.CharField(max_length=255)),
                ('service', models.CharField(choices=[('police', 'Police'), ('fire', 'Fire'), ('nadmo', 'MADMO'), ('ecg', 'ECG')], default='', max_length=20)),
            ],
            options={
                'verbose_name': 'institution',
                'verbose_name_plural': 'instituitions',
                'indexes': [models.Index(fields=['institution_name'], name='account_ins_institu_0f30a2_idx')],
            },
            bases=('account.abstractuserprofile',),
        ),
        migrations.CreateModel(
            name='Emergency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=10)),
                ('location', models.JSONField(blank=True, null=True)),
                ('usage_type', models.CharField(default='', max_length=100)),
                ('location_context', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('town', models.CharField(blank=True, max_length=100, null=True)),
                ('locality', models.CharField(blank=True, max_length=100, null=True)),
                ('mission_status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed')], default='', max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency', to='account.users')),
            ],
        ),
        migrations.CreateModel(
            name='Contacts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email_address', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=20, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('relation', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('contact_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_as_contact', to='account.users')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='account.users')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='abstractuserprofile',
            index=models.Index(fields=['email'], name='account_abs_email_5cdf1c_idx'),
        ),
        migrations.AddIndex(
            model_name='contacts',
            index=models.Index(fields=['first_name', 'last_name', 'email_address', 'phone_number'], name='account_con_first_n_4ec49d_idx'),
        ),
    ]
