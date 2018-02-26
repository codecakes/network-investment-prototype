# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import Susbcription

class SusbcriptionAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(SusbcriptionAdmin, self).__init__(model, admin_site)

admin.site.register(Susbcription, SusbcriptionAdmin)
