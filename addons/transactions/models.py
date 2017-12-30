# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from addons.wallet.models import Wallet
import uuid
# Create your models here.
class Transactions(models.Model):

	sender_wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE, related_name='+')
	reciever_wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE, related_name='+')
	description = models.CharField(max_length=30, null=True, blank=True)
	tx_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	amount = models.FloatField(null=True, blank=True, default=0.0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "%s" %(self.tx_id)