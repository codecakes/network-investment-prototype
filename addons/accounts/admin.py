# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ProfileAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(ProfileAdmin, self).__init__(model, admin_site)

admin.site.register(Profile, ProfileAdmin)
