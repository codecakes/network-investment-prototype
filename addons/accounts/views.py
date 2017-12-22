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
from addons.accounts.models import Profile
from forms import signup_form
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
    def reset_password(self, user, request):
	    c = {
	        'email': user.email,
	        'domain': request.META['HTTP_HOST'],
	        'site_name': 'AVI Crypto',
	        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
	        'user': user,
	        'token': default_token_generator.make_token(user),
	        'protocol': 'http',
	    }
	    subject_template_name = 'password_reset_subject.txt'
	    # copied from
	    # django/contrib/admin/templates/registration/password_reset_subject.txt
	    # to templates directory
	    email_template_name = 'registration_password_reset_email.html'
	    # copied from
	    # django/contrib/admin/templates/registration/password_reset_email.html
	    # to templates directory
	    subject = loader.render_to_string(subject_template_name, c)
	    # Email subject *must not* contain newlines
	    subject = ''.join(subject.splitlines())
	    email = loader.render_to_string(email_template_name, c)
	    send_mail(subject, email, DEFAULT_FROM_EMAIL,
	              [user.email], fail_silently=False)

    def post(self, request, *args, **kwargs):
    	print 'self', self

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
                        return HttpResponse("User is admin user")
                    return HttpResponse("usrertype is staff")
                else:
                    return HttpResponseRedirect('/home')
            	return HttpResponse("login is ok")
            else:
            	return HttpResponse("failed inside")
        else:
        	return HttpResponse("failed outside")
        return HttpResponse("failed extra outside")

def thanks(request):
    template = loader.get_template('thanks.html')
    context = {
            'user':'None'
        }
    return HttpResponse(template.render(context, request))

def logout_fn(request):
   logout(request)
   response = HttpResponseRedirect('/')
   return response

def home(request):
    if request.method == 'GET':
    	context = {
            'user':'None'
        }
        template = loader.get_template('dashboard.html')
        if not request.user.is_authenticated():
            return HttpResponse("Oopse something went wrong")
        else:
            return HttpResponse(template.render(context,request))
    else:
        return HttpResponse('404 not found')