# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from addons.accounts.models import Profile, Members, UserAccount, SupportTicket, Userotp
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import csv
from time import gmtime, strftime
from django.http import HttpResponse, HttpResponseRedirect
from django.http import StreamingHttpResponse

class ProfileAdmin(admin.ModelAdmin):
	actions = ['export_data_in_csv', 'create_manual_withdraw', 'send_notificaion_mail', 'send_notificaion_sms']
		
	search_fields = ('status', 'user', 'user_auto_id')

	list_filter = ['status', 'country', 'email_verified', 'mobile_verified']

	def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(ProfileAdmin, self).__init__(model, admin_site)

	def export_data_in_csv(self, request, queryset):
		# last_date = UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 5)))
		_date = strftime("%c")
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="user-profile.csv"'
		writer = csv.writer(response)
		writer.writerow(['#DOWNLOAD-TYPE','LOCAL', 'User Profile'])
		writer.writerow(['#DOC-TYPE','User Profile Summary'])
		writer.writerow(["DOWNLOAD-DATE", (_date),'UTC'])
		writer.writerow(["@DOWNLOAD-BY", 'Admin'])
		writer.writerow([])
		writer.writerow(["@Profile Meta"])
		writer.writerow(['ID','User ID','First Name', 'Last Name', 'Mobile', 'Email', 'Date of Join', 'Wallet ETH', 'Wallet BTC', 'Wallet XRP'])
		for data in queryset:
			try:
				xrp_address = data.user.useraccount.xrp_address
				xrp_tag = data.user.useraccount.xrp_destination_tag
				btc_address  = data.user.useraccount.btc_address
				eth_address = data.user.useraccount.eth_address
			except:
				xrp_address = 'Not Available'
				xrp_tag = 'Not Available'
				btc_address  = 'Not Available'
				eth_address = 'Not Available'
			print data.user
			writer.writerow([data.id, data.user, data.user.first_name, data.user.last_name, data.user.profile.mobile, data.user.email, data.user.date_joined, eth_address, btc_address, xrp_address, xrp_tag])
		return response
	
	export_data_in_csv.short_description = 'Download Profile'

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
