# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings
import datetime
from dateutil.relativedelta import relativedelta
import uuid

# Create your models here.


class Packages(models.Model):
    package_name = models.CharField(max_length=100, null=True, blank=True)
    package_code = models.CharField(max_length=50, null=True, blank=True)
    payout = models.FloatField(null=True, blank=True, default=0.0)
    directout = models.FloatField(null=True, blank=True, default=0.0)
    binary_payout = models.FloatField(null=True, blank=True, default=0.0)
    capping = models.FloatField(null=True, blank=True, default=0.0)
    no_payout = models.FloatField(null=True, blank=True, default=0.0)
    loyality = models.FloatField(null=True, blank=True, default=0.0)
    roi = models.FloatField(null=True, blank=True, default=0.0)
    price = models.FloatField(null=True, blank=True, default=0.0)
    description = models.TextField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s" % (self.package_name)


class User_packages(models.Model):
    package = models.ForeignKey(Packages, null=True, related_name='+')
    duration = models.IntegerField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    status_choices = (
        ('A', 'Active'),
        ('NA', 'Non-Active'),
        ('C', 'Confirmed'),
        ('NC', 'Non-Confirmed')
    )
    cur_choice = (
        ('btc', 'Bitcoin'),
        ('xrp', 'Ripple'),
        ('eth', 'Ethereum')
    )
    status = models.CharField(
        max_length=50, choices=status_choices, default="NA")
    user = models.ForeignKey(User, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_payout_date = models.DateTimeField(default=settings.EPOCH_BEGIN)
    binary = models.FloatField(null=True, blank=True, default=0.0)
    daily = models.FloatField(null=True, blank=True, default=0.0)
    weekly = models.FloatField(null=True, blank=True, default=0.0)
    direct = models.FloatField(null=True, blank=True, default=0.0)
    total_payout = models.FloatField(null=True, blank=True, default=0.0)
    left_binary_cf = models.FloatField(null=True, blank=True, default=0.0)
    right_binary_cf = models.FloatField(null=True, blank=True, default=0.0)
    paid_txn_id = models.CharField(max_length=100, null=True, blank=True)
    paid_cur = models.CharField(max_length=50, choices=cur_choice, null=True)
    # if criterion reached, enable binary
    binary_enable = models.NullBooleanField(default=False, null=True, blank=True)
    


    def save(self, *args, **kwargs):
        if not self.pk:
            days = datetime.timedelta(days=self.package.no_payout*7)
            self.expiry_date = datetime.date.today() + days
            self.duration = self.package.no_payout

        super(User_packages, self).save(*args, **kwargs)
