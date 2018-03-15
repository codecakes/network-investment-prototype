# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import Packages, User_packages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import csv
from time import gmtime, strftime
from django.http import HttpResponse, HttpResponseRedirect
from django.http import StreamingHttpResponse
from addons.packages.lib.payout import calc_binary, calc_direct, calc_weekly


class PackagesAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(PackagesAdmin, self).__init__(model, admin_site)

class UserPackagesAdmin(admin.ModelAdmin):
	actions = ['export_data_in_csv']

	def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(UserPackagesAdmin, self).__init__(model, admin_site)

	def export_data_in_csv(self, request, queryset):
		_date = strftime("%c")
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="user-packages.csv"'
		writer = csv.writer(response)
		writer.writerow(['#DOWNLOAD-TYPE','LOCAL', 'User Packages'])
		writer.writerow(['#DOC-TYPE','User Packages Summary'])
		writer.writerow(["DOWNLOAD-DATE", (_date),'UTC'])
		writer.writerow(["@DOWNLOAD-BY", 'Admin'])
		writer.writerow([])
		writer.writerow(["@Package Meta"])
		writer.writerow(['ID','User ID','First Name', 'Last Name', 'Mobile', 'Email', 'Date of Join', 'Package', 'Package Activation date', 'Package Status' ,'Binary', 'Direct', 'Weekly', 'Total Payout', 'Paid Cur'])
		for data in queryset:
			if data.status == 'A':
				status = 'Active'
			else:
				status = 'Not-Active'
			user_direct = calc_direct(data.user, None, None)[0]
			user_binary = calc_binary(data.user, None, None)[0][0]
			user_weekly = calc_weekly(data.user, None, None)[0]
			total_payout = user_direct + user_binary + user_weekly
			writer.writerow([data.id, data.user, data.user.first_name, data.user.last_name, data.user.profile.mobile, data.user.email, data.user.date_joined, data.package, data.created_at, status ,user_binary, user_direct, user_weekly, total_payout, data.paid_cur])
		return response

	export_data_in_csv.short_description = 'Export'

admin.site.register(Packages, PackagesAdmin)
admin.site.register(User_packages, UserPackagesAdmin)



