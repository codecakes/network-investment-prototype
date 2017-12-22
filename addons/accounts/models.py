# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
# Create your models here.

class Profile(models.Model):
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	referal_id = models.TextField(max_length=500, blank=True)
	sponser_id =models.CharField(null=True,max_length=300)
	package = models.DateField(null=True,blank=True)
	mobile = models.CharField(max_length=15,validators=[phone_regex], blank=True)
	placement_id = models.CharField(null=True, blank=True, max_length=15)

	def __unicode__(self):
		return "%s" %(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
