# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class Susbcription(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

    name = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=15,validators=[phone_regex], blank=True)
    email = models.CharField(max_length=15, null=True, blank=True)