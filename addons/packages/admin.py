# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import Packages, User_packages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class PackagesAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(PackagesAdmin, self).__init__(model, admin_site)

class UserPackagesAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(UserPackagesAdmin, self).__init__(model, admin_site)


admin.site.register(Packages, PackagesAdmin)
admin.site.register(User_packages, UserPackagesAdmin)