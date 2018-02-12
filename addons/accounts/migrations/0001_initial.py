# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-09 18:26
from __future__ import unicode_literals

import addons.accounts.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('document', models.FileField(upload_to='documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('parent_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_auto_id', models.CharField(blank=True, default=addons.accounts.models.increment_user_id, max_length=500, null=True)),
                ('referal_code', models.CharField(blank=True, max_length=20)),
                ('country', models.CharField(blank=True, default=None, max_length=5, null=True)),
                ('mobile', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('placement_position', models.CharField(choices=[('L', 'Left'), ('R', 'Right')], max_length=100, null=True)),
                ('bank_name', models.CharField(max_length=20, null=True)),
                ('account_number', models.CharField(max_length=20, null=True)),
                ('account_type', models.CharField(max_length=20, null=True)),
                ('account_name', models.CharField(max_length=20, null=True)),
                ('my_referal_code', models.CharField(max_length=20, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('NA', 'Non-Active'), ('C', 'Confirmed'), ('NC', 'Non-Confirmed')], max_length=50)),
                ('model_pic', models.ImageField(default='media/pic_folder/None/no-img.jpg', upload_to='media/pic_folder')),
                ('href', models.CharField(max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('token', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('placement_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sponser_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('P', 'Pending'), ('C', 'Confirmed')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('btc_address', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('xrp_address', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('eth_address', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('eth_destination_tag', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
