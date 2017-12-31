# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid
# Create your models here.
class Packages(models.Model):

	package_name = models.CharField(max_length=100, null=True, blank=True)
	package_code = models.CharField(max_length=50, null=True, blank=True)
	payout = models.CharField(max_length=50, null=True, blank=True)
	directout = models.CharField(max_length=50, null=True, blank=True)
	binary_payout = models.CharField(max_length=50, null=True, blank=True)
	capping = models.CharField(max_length=50, null=True, blank=True)
	no_payout = models.CharField(max_length=50, null=True, blank=True)
	loyality = models.CharField(max_length=50, null=True, blank=True)	
	roi = models.CharField(max_length=50, null=True, blank=True)
	price = models.FloatField(null=True, blank=True, default=0.0)
	description = models.TextField(null=True,blank=True)
	uuid = models.CharField(max_length=50, default=uuid.uuid4, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return "%s" %(self.package_name)

class User_packages(models.Model):
	package = models.ForeignKey(Packages, null=True, related_name='+')
	package_duration = models.CharField(max_length=50, null=True, blank=True)
	expiry_date = models.DateTimeField(null=True)
	status = models.CharField(max_length=50, null=True, blank=True)
	user_id = models.ForeignKey(User, null=True, related_name='+')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
