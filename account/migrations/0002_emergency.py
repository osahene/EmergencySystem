# Generated by Django 4.2.16 on 2024-11-16 22:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Emergency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=10)),
                ('location', models.JSONField()),
                ('country', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('town', models.CharField(max_length=100)),
                ('locality', models.CharField(max_length=100)),
                ('mission_status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed')], default='', max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency', to='account.users')),
            ],
        ),
    ]