# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from models import Profile
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.views.generic import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from addons.accounts.models import Profile
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.models import Packages
from forms import signup_form
from django.shortcuts import get_object_or_404

# Create your views here.

def index(request):
	if request.method == 'GET':
		# import pdb; pdb.set_trace()
		context = {
			'User':'None',
			'packages':[
                        (100, 4.00, 36, 5.00, 3.00, 100),
                        (500, 5.00, 35, 5.50, 3.00, 500),
                        (1000, 7.00, 35, 6.00, 3.50, 1000),
                        (5000, 7.50, 35, 6.50, 3.75, 5000),
                        (10000, 8.00, 33, 7.00, 4.00, 20000),
                        (35000, 8.25, 32, 7.50, 4.00, 50000),
                        (50000, 8.50, 32, 8.50, 4.00, 75000),
                        (100000, 9.00, 31, 8.00, 4.00, 100000)
                    ]
		}
		template = loader.get_template('index.html')
		return HttpResponse(template.render(context,request))
	if request.method == 'POST':
		# pass
		return HttpResponse("index post")

class Registration(FormView):    # code for template is given below the view's code
    template_name = "login.html"
    success_url = '/thanks'
    form_class = signup_form

    @staticmethod
    def validate_email_address(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
    def post(self, request, *args, **kwargs):
    	form = self.form_class(request.POST)
    	try:
    		if form.is_valid():
    			data_dict = form.cleaned_data
    			data = form.cleaned_data['email']
    			if self.validate_email_address(data) is True:
    				associated_users = User.objects.filter(
    					Q(email=data) | Q(username=data))
    				if associated_users.exists():
    					result = self.form_valid(form)
    					messages.success(
    						request, 'User already exists')
    					return result
    				else:
    					user = User.objects.create(username=data_dict['email'], email=data_dict['email'],password=data_dict['password'], first_name=data_dict['name'])
    					result = self.form_valid(form)
                        messages.success(
                            request, 'An email has been sent to {0}. Please check its inbox to continue reseting password.'.format(data))
                        return result
   #              else:
   #              	result = self.form_invalid(form)
   #              	messages.error(
   #              		request, 'Error')
   #              	return result
			# else:
   #          	result =  self.form_invalid(form)
			# 	messages.error(
   #                          request, 'Email is not correct')
   #              return result

    	except Exception as e:
    		raise
    	# print 'self', self
    	return self.form_invalid(form)

def login_fn(request):
	if request.method == 'GET':
		template = loader.get_template('login.html')
		context = {
			'user':'None'
		}
		return HttpResponse(template.render(context,request))
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_staff:
                    if user.is_superuser:
                        return HttpResponseRedirect('/admin')
                    return HttpResponseRedirect("/home")
                else:
                    return HttpResponseRedirect('/home')
            	return HttpResponseRedirect('/home')
            else:
            	return HttpResponseRedirect('/error')
        else:
        	return HttpResponseRedirect('/error')
        return HttpResponseRedirect('/error')

def thanks(request):
    template = loader.get_template('thanks.html')
    context = {
            'user':'None'
        }
    #return HttpResponse(template.render(context, request))
    return HttpResponse("THank tou for registration.Admin")

def error(request):
    template = loader.get_template('error.html')
    context = {
            'user':'None'
        }
    return HttpResponse(template.render(context, request))

def logout_fn(request):
   logout(request)
   response = HttpResponseRedirect('/')
   return response

@login_required(login_url="/login")
def home(request):
    if request.method == 'GET':
        user = request.user
        user_d = User.objects.filter(id=user.id)
        packages = Packages.objects.filter(user=request.user)
        # # import pdb; pdb.set_trace()
        # # transactions = Transactions.objects.filter(sender_wallet=get_object_or_404(Wallet, owner=request.user))
        # try:
        #     # sender_wallet= Wallet.objects.get(owner=request.user)
        #     transactions = Transactions.objects.filter()
        # except Transactions.DoesNotExist:
        #     transactions = None
        try:
            wallets = Wallet.objects.filter(owner=request.user)
        except:
            wallets = None
        # profile = Profile.objects.filter(user=request.user)
    	context = {
            'user':user_d,
            'wallets':wallets,
            # # 'profile':profile,
            # 'transactions':transactions,
            'packages':packages
        }
        # import pdb; pdb.set_trace()
        print context
        template = loader.get_template('dashboard.html')
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/error')
        else:
            return HttpResponse(template.render(context,request))
    else:
        return HttpResponseRedirect('/error')