# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from addons.packages.models import Packages
import base64, uuid
from django.contrib.postgres.fields import ArrayField

# Create your models here.
# User._meta.local_fields[4].__dict__['_unique'] = True

def increment_user_id():
	last_user_id = Profile.objects.all().order_by('user_auto_id').last()
	if last_user_id is  None:
		return 'AVI000000001'
	# if not last_user_id.user_auto_id:
	#      return 'AVI000000001'
	else:
		user_id_no = last_user_id.user_auto_id
		user_id_int = int(user_id_no.split('AVI')[-1])
		new_user_id_int = user_id_int + 1
		new_user_id_no = 'AVI' + str(new_user_id_int).zfill(9)
		return new_user_id_no

class Profile(models.Model):
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	placement_type = (
		('L', 'Left'),
		('R', 'Right')
	)
	status_type = (
		('A', 'Active'),
		('NA', 'Non-Active'),
		('C', 'Confirmed'),
		('NC', 'Non-Confirmed')
	)
	user_auto_id = models.CharField(max_length=500, default=increment_user_id, null=True, blank=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	referal_code = models.CharField(max_length=20, blank=True)
	sponser_id = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+', null=True)
	country = models.CharField(max_length=5, default=None, null=True, blank=True)
	mobile = models.CharField(max_length=15,validators=[phone_regex], blank=True)
	placement_id = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+', null=True)
	placement_position = models.CharField(max_length=100,choices=placement_type, null=True)
	bank_name = models.CharField(max_length=20, null=True)
	account_number = models.CharField(max_length=20, null=True)
	account_type = models.CharField(max_length=20, null=True)
	account_name = models.CharField(max_length=20, null=True)
	my_referal_code = models.CharField(max_length=20, null=True)
	status = models.CharField(max_length=50, choices=status_type)
	model_pic = models.ImageField(upload_to = 'media/pic_folder', default = 'media/pic_folder/None/no-img.jpg')
	href = models.CharField(max_length=20, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	token = models.CharField(max_length=100, default=None, null=True, blank=True)
	otp = models.CharField(max_length=10, default=None, null=True, blank=True)
	email_verified = models.NullBooleanField(default=True, null=True, blank=True)
	mobile_verified = models.NullBooleanField(default=True, null=True, blank=True)

	def __unicode__(self):
		return "%s" %(self.user)

	def generate_referal_code(self):
		return base64.urlsafe_b64encode(uuid.uuid1().bytes.encode("base64").rstrip())[:15]

	def save(self, *args, **kwargs):
		if not self.pk:
			self.my_referal_code = self.generate_referal_code()
		elif not self.my_referal_code:
			self.my_referal_code = self.generate_referal_code()

		# self.user.username = self.user_auto_id
		# self.user.save()

		return super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile = Profile.objects.create(user=instance)
		instance.username = profile.user_auto_id
		instance.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class Members(models.Model):
	parent_id = models.ForeignKey(User, related_name='+', null=True)
	child_id = models.ForeignKey(User, related_name='+', null=True)

class Document(models.Model):
	description = models.CharField(max_length=255, blank=True)
	document = models.FileField(upload_to='documents/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

class SupportTicket(models.Model):
	user = models.ForeignKey(User, related_name='+', null=True)
	description = models.TextField()
	status_choices = (
		('P', 'Pending'),
		('C', 'Confirmed'),
	)
	status = models.CharField(max_length=50, choices=status_choices)
	created_at = models.DateTimeField(auto_now_add=True)

class UserAccount(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	btc_address = models.CharField(max_length=100, default=None, null=True, blank=True)
	xrp_address = models.CharField(max_length=100, default=None, null=True, blank=True)
	eth_address = models.CharField(max_length=100, default=None, null=True, blank=True)
	eth_destination_tag = models.CharField(max_length=100, default=None, null=True, blank=True)
	xrp_destination_tag = models.CharField(max_length=100, default=None, null=True, blank=True)
	btc_destination_tag = models.CharField(max_length=100, default=None, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Userotp(models.Model):
	otp = models.CharField(max_length=6, default=None, null=True, blank=True)
	time = models.DateTimeField(auto_now_add=True)
	mobile = models.CharField(max_length=15, blank=True)
	user = models.ForeignKey(User, related_name='+', null=True)
	otp_type = (
		('login', 'login'),
		('signup', 'signup'),
		('mobile', 'mobile'),
		('withdraw', 'withdraw'),
		('buy', 'buy'),
	)
	otp_status = (
		('active', 'active'),
		('expire', 'expire')
	)	
	type = models.CharField(max_length=10, default=None, null=True, blank=True, choices=otp_type)
	status = models.CharField(max_length=10, default=None, null=True, blank=True, choices=otp_status)
	

# CREATE TABLE "accounts_userotp" ("id" serial NOT NULL PRIMARY KEY,"otp" varchar(30) NOT NULL,"time" timestamp NOT NULL,"mobile" varchar(60) NOT NULL,"type" varchar(30) NOT NULL,"status" varchar(50) NOT NULL,);