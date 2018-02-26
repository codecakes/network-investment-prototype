# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import Context, RequestContext, loader
from django.template.loader import get_template, render_to_string
from models import Susbcription
import json
from django.views.decorators.csrf import csrf_exempt

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
        sub_data = Susbcription.objects.create(name=data['name'],country=data['country'],mobile=data['mobile'],email=data['email'])
        content = {
                "status": "success",
                "message": "Thanks for susbcribing our avibank."
            }
        return HttpResponse(json.dumps(content))