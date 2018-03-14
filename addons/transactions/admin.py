# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import Transactions
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from time import gmtime, strftime
from django.http import HttpResponse, HttpResponseRedirect
from django.http import StreamingHttpResponse
import csv
class TransactionsAdmin(admin.ModelAdmin):
	actions = ['export_data_in_csv', 'export_all_in_csv']
	
	search_fields = ('status', 'tx_type')
	
	list_filter = ['created_at', 'tx_type', 'status']

	def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(TransactionsAdmin, self).__init__(model, admin_site)

	def export_data_in_csv(self, request, queryset):
		_date = strftime("%c")
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Transactions.csv"'
		writer = csv.writer(response)
		writer.writerow(['#DOWNLOAD-TYPE','LOCAL', 'Transactions'])
		writer.writerow(['#DOC-TYPE','Transactions Summary'])
		writer.writerow(["DOWNLOAD-DATE", (_date),'UTC'])
		writer.writerow(["@DOWNLOAD-BY", 'Admin'])
		writer.writerow([])
		writer.writerow(["@Transactions Meta"])
		writer.writerow(['Transations ID', 'Transactions Date', 'Sender', 'User ID','First Name', 'Last Name', 'Mobile', 'Email',  'Status', 'Transactions Type','Amount'])
		for data in queryset:
			if data.tx_type == 'W':
				writer.writerow([data.tx_id, data.created_at, data.sender_wallet.owner, data.reciever_wallet.owner, data.reciever_wallet.owner.first_name, data.reciever_wallet.owner.last_name, data.reciever_wallet.owner.profile.mobile, data.reciever_wallet.owner.email, data.get_status_display(), data.get_tx_type_display(), data.amount])
		return response
	
	def export_all_in_csv(self, request, queryset):
		_date = strftime("%c")
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Transactions.csv"'
		writer = csv.writer(response)
		writer.writerow(['#DOWNLOAD-TYPE','LOCAL', 'Transactions'])
		writer.writerow(['#DOC-TYPE','Transactions Summary'])
		writer.writerow(["DOWNLOAD-DATE", (_date),'UTC'])
		writer.writerow(["@DOWNLOAD-BY", 'Admin'])
		writer.writerow([])
		writer.writerow(["@Transactions Meta"])
		writer.writerow(['Transations ID', 'Transactions Date', 'Sender', 'User ID','First Name', 'Last Name', 'Mobile', 'Email',  'Status', 'Transactions Type','Amount'])
		for data in queryset:
			writer.writerow([data.tx_id, data.created_at, data.sender_wallet.owner, data.reciever_wallet.owner, data.reciever_wallet.owner.first_name, data.reciever_wallet.owner.last_name, data.reciever_wallet.owner.profile.mobile, data.reciever_wallet.owner.email, data.get_status_display(), data.get_tx_type_display(), data.amount])
		return response

	export_data_in_csv.short_description = 'Export Withdraw Data'
	export_all_in_csv.short_description = 'Export All Data'

admin.site.register(Transactions, TransactionsAdmin)

# 	type_choices = (
# 		('W', 'Withdraw'),
# 		('P', 'Add Package'),
# 		('U', 'User to User'),
# 		('topup', 'Top-up'),
# 		('roi', 'ROI'),
# 		('binary', 'Binary'),
# 		('direct', 'Direct'),
# 	)