# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from addons.accounts.models import Profile, Members, UserAccount, SupportTicket, Userotp
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ProfileAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(ProfileAdmin, self).__init__(model, admin_site)

class MemberAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(MemberAdmin, self).__init__(model, admin_site)

class UserAccountAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(UserAccountAdmin, self).__init__(model, admin_site)
		
class SupportTicketAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(SupportTicketAdmin, self).__init__(model, admin_site)

class OtpAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(OtpAdmin, self).__init__(model, admin_site)
		
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Members, MemberAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(SupportTicket, SupportTicketAdmin)
admin.site.register(Userotp, OtpAdmin)
