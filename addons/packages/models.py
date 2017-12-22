# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid
# Create your models here.
class Packages(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	price = models.FloatField(null=True, blank=True, default=0.0)
	description = models.TextField(null=True,blank=True)
	expiry_status = models.CharField(max_length=10, null=True, blank=True)
	expiry_date = models.DateTimeField(null=True)
	# purchased = ArrayField(ArrayField(models.IntegerField()))
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return "%s" %(self.user)