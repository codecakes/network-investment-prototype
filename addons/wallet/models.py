# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import uuid
# Create your models here.
class Wallet(models.Model):

	wallet_type_choice = (
	    ('BN', 'Binary'),
	    ('DR', 'Direct'),
	    ('ROI', 'ROI'),
	    ('AW', 'Avi Wallet'),
		('XRP', 'XRP'),
		('BTC', 'BTC'),
		('ETH', 'ETH'),
	)

	owner = models.ForeignKey(User,on_delete=models.CASCADE, related_name='+')
	wallet_type = models.CharField(max_length=100, choices=wallet_type_choice)
	description = models.CharField(null=True, max_length=300)
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	amount = models.FloatField(null=True, blank=True, default=0.0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "%s" %(self.uuid)
