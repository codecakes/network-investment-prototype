# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import Context, RequestContext, loader
from django.template.loader import get_template, render_to_string
from models import Susbcription
import json

# Create your views here.
def index(request):
    if request.method == 'GET':
        context = {
            'user':None
        }
        template = loader.get_template('avibank/index.html')
        return HttpResponse(template.render(context, request))
    else:
        data = request.data
        sub_data = Susbcription.objects.create(name=data['name'],country=data['country'],phone=data['phone'],email=data['email'])
        content = {
                "status": "success",
                "message": "We will send notification."
            }
        return HttpResponse(json.dumps(content))