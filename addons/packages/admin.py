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
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
import datetime, pytz
from avicrypto import services
from django.conf import settings
from django.template.loader import get_template, render_to_string
EPOC = settings.EPOCH_BEGIN

class PackagesAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
		self.list_display = [field.name for field in model._meta.fields]
		super(PackagesAdmin, self).__init__(model, admin_site)

class UserPackagesAdmin(admin.ModelAdmin):
	actions = ['export_data_in_csv', 'create_manual_withdraw', 'send_notificaion_mail', 'send_notificaion_sms']
	
	search_fields = ('status', 'user')

	list_filter = ['created_at', 'status', 'package']

	list_display = []
	
	def __init__(self, model, admin_site):
		self.list_display.extend([field.name for field in model._meta.fields])
		self.list_display.insert(13, self.total)
		super(UserPackagesAdmin, self).__init__(model, admin_site)

	

	def total(self,obj):
		# import pdb; pdb.set_trace()
		total_value =  obj.binary + obj.direct + obj.weekly
		return total_value

	total.short_description = 'Total Amount'
	def send_notificaion_mail(self, request, queryset):
		for data in queryset:
			email_data = {
							"user": data.user.first_name,
						}
			body = render_to_string('mail/alert.html', email_data)
			try:
				email = data.user.email
			except:
				email = 'admin@avicrypto.us'
			services.send_email_mailgun(
				'Important Notice - Payout release downtime ', body, email, from_email="postmaster")
	def send_notificaion_sms(self, request, queryset):
		pass
	def export_data_in_csv(self, request, queryset):
		UTC = pytz.UTC	
		next_date = UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 12)))
		last_date = EPOC
		# last_date = UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 5)))
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
			user_direct = data.direct
			user_binary = data.binary
			user_weekly = data.weekly
			total_payout = user_direct + user_binary + user_weekly
			writer.writerow([data.id, data.user, data.user.first_name, data.user.last_name, data.user.profile.mobile, data.user.email, data.user.date_joined, data.package, data.created_at, status ,user_binary, user_direct, user_weekly, total_payout, data.paid_cur])
		return response
	def create_manual_withdraw(self, request, queryset):
		UTC = pytz.UTC	
		next_date = UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 12)))
		last_date = EPOC
		created_at = UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 13, 5,00,00)))
		for data in queryset:
			user = data.user
			avi_owner_wallet_btc = Wallet.objects.filter(owner=request.user, wallet_type='BTC').first()
			avi_owner_wallet_eth = Wallet.objects.filter(owner=request.user, wallet_type='ETH').first()
			avi_owner_wallet_xrp = Wallet.objects.filter(owner=request.user, wallet_type='XRP').first()
			wallet_BTC = Wallet.objects.get_or_create(owner=user, wallet_type='BTC')
			try:
				wallet_XRP = Wallet.objects.get_or_create(owner=user, wallet_type='XRP')
			except:
				wallet_XRP = Wallet.objects.filter(owner=user, wallet_type='XRP')
			wallet_ETH = Wallet.objects.get_or_create(owner=user, wallet_type='ETH')
			total_payout = calc_direct(data.user, last_date, next_date)[0] + calc_binary(data.user, last_date, next_date)[0][0] + calc_weekly(data.user, last_date, next_date)[0]
			txn = Transactions.objects.create(sender_wallet=avi_owner_wallet_btc, reciever_wallet=wallet_BTC[0], amount=total_payout, tx_type='W', status='processing')
			txn.created_at = created_at
			txn.save()

	send_notificaion_mail.short_description = 'Send mail'
	send_notificaion_sms.short_description = 'Send SMS'
	export_data_in_csv.short_description = 'Export'
	create_manual_withdraw.short_description = "Manual Withdraw Create (We don't suggest to use manual withdraw create )"
admin.site.register(Packages, PackagesAdmin)
admin.site.register(User_packages, UserPackagesAdmin)
