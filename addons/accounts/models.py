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
User._meta.local_fields[4].__dict__['_unique'] = True

# def increment_user_id():
#     last_user_id = Profile.objects.all().order_by('user_auto_id').last()
#     if not last_user_id.user_auto_id:
#          return 'AVI000001'
#     user_id_no = last_user_id.user_auto_id
#     user_id_int = int(user_id_no.split('AVI')[-1])
#     new_user_id_int = user_id_int + 1
#     new_user_id_no = 'AVI' + str(new_user_id_int)
#     return new_user_id_no
    
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
	user_auto_id = models.CharField(max_length=500, default='0000', null=True, blank=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	referal_code = models.CharField(max_length=20, blank=True)
	# sponser_id =models.OneToOneField(User, null=True, related_name='+')
	sponser_id = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+', null=True)
	# package = models.OneToOneField(Packages,null=True)
	mobile = models.CharField(max_length=15,validators=[phone_regex], blank=True)
	placement_id = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+', null=True)
	# placement_id = models.OneToOneField(User, null=True, related_name='+')
	placement_position = models.CharField(max_length=100,choices=placement_type, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	bank_name = models.CharField(max_length=20, null=True)
	account_number = models.CharField(max_length=20, null=True)
	account_type = models.CharField(max_length=20, null=True)
	account_name = models.CharField(max_length=20, null=True)
	my_referal_code = models.CharField(max_length=20, null=True)
	status = models.CharField(max_length=50, choices=status_type)
	image = models.FileField(upload_to='documents/', null=True)
	href = models.CharField(max_length=20, null=True)
	# members = ArrayField(ArrayField(models.CharField(max_length=10, blank=True),size=8,),size=8,)

	def __unicode__(self):
		return "%s" %(self.user)

	def generate_referal_code(self):
		return base64.urlsafe_b64encode(uuid.uuid1().bytes.encode("base64").rstrip())[:15]

	def save(self, *args, **kwargs):
		if not self.pk:
			self.my_referal_code = self.generate_referal_code()
		elif not self.my_referal_code:
			self.my_referal_code = self.generate_referal_code()
		return super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

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