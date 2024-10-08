# Generated by Django 5.1 on 2024-08-29 13:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_remove_customuser_date_joined_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserKYC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aadhar_card_number', models.CharField(blank=True, max_length=12, null=True, unique=True)),
                ('aadhar_card_image', models.ImageField(blank=True, null=True, upload_to='kyc/adhaar')),
                ('pan_card_number', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('pan_card_image', models.ImageField(blank=True, null=True, upload_to='kyc/pan')),
                ('is_verified', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('verification_method', models.CharField(choices=[('aadhar_card', 'Aadhar card'), ('pan_card', 'Pan card')], max_length=11)),
                ('submission_date', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
