# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import Context, RequestContext, loader
from django.template.loader import get_template, render_to_string
from models import Susbcription
import json, re
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from avicrypto import services
# Create your views here.
@csrf_exempt
def index(request):
    if request.method == 'GET':
        context = {
            'user':None
        }
        template = loader.get_template('avibank/index.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        data = request.POST
        if data['email'] and validate_email(data['email']) == None:
            if re.match(r'^\+?1?\d{9,15}$', data['mobile']):
                sub_data = Susbcription.objects.create(name=data['name'],country=data['country'],mobile=data['mobile'],email=data['email'])
                email_data = {
                        "user": data['name'],
                    }
                body = render_to_string('avibank/mail/avibank_subscribe_mail.html', email_data)
                services.send_email_mailgun(
                        'Welcome to Avicrypto', body, data['email'], from_email="postmaster")
                content = {
                        "status": "success",
                        "message": "Thanks for susbcribing our avibank."
                }
                return HttpResponse(json.dumps(content))
            else:
                content = {
                        "status": "error",
                        "message": "Mobile number is not correct."
                    }
                return HttpResponse(json.dumps(content))
        else:
            content = {
                        "status": "error",
                        "message": "Email is not correct."
                    }
            return HttpResponse(json.dumps(content))


        # if email and validate_email(email) == None:
        #     first_name = request.POST.get('first_name')
        #     last_name = request.POST.get('last_name')
        #     mobile = request.POST.get('mobile')
        #     password = request.POST.get('password')

        #     if re.match(r'^\+?1?\d{9,15}$', mobile):