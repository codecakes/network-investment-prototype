# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from addons.packages.models import Packages
# Create your models here.
User._meta.local_fields[4].__dict__['_unique'] = True

class Profile(models.Model):
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	referal_code = models.TextField(max_length=500, blank=True)
	sponser_id =models.OneToOneField(User, null=True, related_name='+')
	package = models.OneToOneField(Packages,null=True)
	mobile = models.CharField(max_length=15,validators=[phone_regex], blank=True)
	placement_id = models.OneToOneField(User, null=True, related_name='+')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	bank_name = models.CharField(max_length=20, null=True)
	account_number = models.CharField(max_length=20, null=True)
	account_type = models.CharField(max_length=20, null=True)
	account_name = models.CharField(max_length=20, null=True)

	def __unicode__(self):
		return "%s" %(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
