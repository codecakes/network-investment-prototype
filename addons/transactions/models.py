# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from addons.wallet.models import Wallet
import uuid

from django.db.models import Q


# Create your models here.

class Transactions(models.Model):

	tx_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	sender_wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE, related_name='+')
	reciever_wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE, related_name='+')
	description = models.CharField(max_length=30, null=True, blank=True)
	amount = models.FloatField(null=True, blank=True, default=0.0)

	status_choices = (
		('P', 'Pending'),
		('C', 'Confirmed'),
		('processing', 'Processing'),
		('paid', 'Paid'),
		('cancel', 'Canceled'),
		('fail', 'Failed')
	)
	status = models.CharField(max_length=50, choices=status_choices, null=True, blank=True, default="P")

	type_choices = (
		('W', 'Withdraw'),
		('P', 'Add Package'),
		('U', 'User to User'),
		('topup', 'Top-up'),
		('roi', 'ROI'),
		('binary', 'Binary'),
		('direct', 'Direct'),
	)
	tx_type = models.CharField(max_length=50, choices=type_choices, null=True, blank=True, default="W")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "%s" %(self.tx_id)
