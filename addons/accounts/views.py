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
from addons.accounts.models import Profile, Members
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.models import Packages, User_packages
from forms import signup_form
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import sys

sys.path.append(settings.BASE_DIR)
from avicrypto import services
# Create your views here.

import json
from lib.tree import load_users, find_min_max


def index(request):
    if request.method == 'GET':
        # import pdb; pdb.set_trace()
        context = {
            'User': 'None',
            'packages': [
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
        template = loader.get_template('index2.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        # pass
        return HttpResponse("index post")


class Registration(FormView):  # code for template is given below the view's code
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
                        user = User.objects.create(username=data_dict['email'], email=data_dict['email'], first_name=data_dict['name'])
                        user.set_password(str(data_dict['password']))
                user.save()
                update_profile(user, request.POST)
                body = "Welcome to Avicrypto! "
                services.send_email_mailgun('Wellcome to Avicrypto', body, data_dict['email'], from_email="postmaster")
                result = self.form_valid(form)
                messages.success(
                    request,
                    'An email has been sent to {0}. Please check its inbox to continue reseting password.'.format(data))
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
        if 'ref' not in request.GET:
            referal = ''
            sponser_id = ''
        else:
            referal = request.GET['ref']
            sponser_id = Profile.objects.filter(my_referal_code=referal)
            sponser_id = sponser_id[0].user_auto_id
            # placement_id = sponser_id[0].user_auto_id
        context = {
            'user': 'None',
            'referal': referal,
            'sponser_id': sponser_id,
            'placement_id': sponser_id
        }
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print request.POST
        user = authenticate(username=username, password=password)
        print user
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
        'user': 'None'
    }
    # return HttpResponse(template.render(context, request))
    return HttpResponse("Thank you for registration.Soon you will receive a conformation mail.")


def error(request):
    template = loader.get_template('error.html')
    context = {
        'user': 'None'
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
        packages = User_packages.objects.filter(user_id=request.user)
        for l in user_d:    code = l.profile.my_referal_code
        context = {
            'user': user_d,
            'request': request,
            'link': request.META['HTTP_HOST'] + '/login?ref=' + str(code),
            'packages': packages
        }

        template = loader.get_template('dashboard.html')
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/error')
        else:
            return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/error')


@login_required(login_url="/login")
@csrf_exempt
def profile(request):
    if request.method == 'GET':
        user = request.user
        user_d = User.objects.filter(id=user.id)

        context = {
            'user': user_d
        }
        template = loader.get_template('profile.html')
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/error')
        else:
            return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        data = request.POST
        email = data['email_id']
        user = User.objects.create(email=email, username=email)
        user.first_name = data['name']
        user.save()
        profile = Profile.objects.get(user=user)
        sponser_id = Profile.objects.get(user_auto_id=data['refer_id'])
        placement_id = Profile.objects.get(user_auto_id=data['place_id'])
        profile.sponser_id = sponser_id.user
        profile.placement_id = placement_id.user
        profile.placement = data['placement']
        profile.save()
        memeber = Members.objects.create(parent_id=placement_id.user, child_id=user)
        return HttpResponse('Success')
    else:
        return HttpResponseRedirect('/error')


@csrf_exempt
def support(request):
    if request.method == 'GET':
        template = loader.get_template('support.html')
        context = {'user': 'None'}
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        services.support_mail('Support Ticket', "Hello, Admin, support ticket generated, please respond",
                              'jain.atul43@gmail.com', from_email="postmaster")
        return HttpResponse('Mail sent to adminstrator', content_type="application/json")


@csrf_exempt
def network(request):
    if request.method == 'GET':
        template = loader.get_template('network.html')
        context = {'user': 'None'}
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        data = traverse_tree(request.user)
        # data =  '{"text":{"name":"Mark Hill","title":"Chief executive officer"},"children":[{"text":{"name":"Joe Linux","title":"Chief Technology Officer"},"children":[{"text":{"name":"Ron Blomquist","title":"Chief Information Security Officer"}},{"text":{"name":"Michael Rubin","title":"Chief Innovation Officer","contact":"we@aregreat.com"}}]},{"text":{"name":"Linda May","title":"Chief Business Officer"},"children":[{"text":{"name":"Alice Lopez","title":"Chief Communications Officer"}},{"text":{"name":"Mary Johnson","title":"Chief Brand Officer"},"children":[{"text":{"name":"Erica Reel","title":"Chief Customer Officer"}}]}]}]}'
        return HttpResponse(data)


# def simple_upload(request):
#     if request.method == 'POST' and request.FILES['myfile']:
#         myfile = request.FILES['myfile']
#         fs = FileSystemStorage()
#         filename = fs.save(myfile.name, myfile)
#         uploaded_file_url = fs.url(filename)
#         return render(request, 'core/simple_upload.html', {
#             'uploaded_file_url': uploaded_file_url
#         })
#     return render(request, 'core/simple_upload.html')

def simple_upload(request):
    if request.method == 'POST' and request.FILES['passfront'] and request.FILES['passback'] and request.FILES[
        'passphoto']:
        passfront = request.FILES['passfront']
        passback = request.FILES['passback']
        passphoto = request.FILES['passphoto']
        fs = FileSystemStorage()
        filename_passfront = fs.save(passfront.name, passfront)
        filename_passback = fs.save(passback.name, passback)
        filename_passphoto = fs.save(passphoto.name, passphoto)
        uploaded_file_url = fs.url(filename_passfront) or fs.url(filename_passback) or fs.url(filename_passphoto)
        return render(request, 'simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'simple_upload.html')


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'model_upload.html', {
        'form': form
    })


def update_profile(user, data):
    profile = Profile.objects.get(user=user)
    profile.mobile = data.get('mobile', None)

    referal_code = data.get('referal', None)
    sponcer_id = data.get('sponcer_id', None)
    placement_id = data.get('placement_id', None)
    placement_position = data.get('placement_position', "L")

    if referal_code:
        user_object = User.objects.get(my_referal_code=referal_code)
        if user_object:
            profile.placement_position = placement_position
            profile.placement_id = User.objects.get(user_auto_id=placement_id)
            profile.referal_code = referal_code
            profile.sponcer_id = user_object

    profile.save()


def traverse_tree(user):
    ref_code = "/add/user?ref={}&place={}".format(user.profile.my_referal_code, user.profile.user_auto_id)
    data = load_users(user, ref_code)
    return json.dumps(data)


@csrf_exempt
def add_user(request):
    if request.method == 'GET':

        if 'ref' not in request.GET:
            referal = ''
            sponser_id = ''
        else:
            referal = request.GET['ref']
            sponser_id = Profile.objects.filter(my_referal_code=referal)
            sponser_id = sponser_id[0].user_auto_id
            pos = request.GET['pos']
            placement_id = request.GET['parent_placement_id']
        context = {
            'user': 'None',
            'referal': referal,
            'sponser_id': sponser_id,
            'placement_id': placement_id,
            'pos': pos
        }
        template = loader.get_template('add-user.html')
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/error')
        else:
            return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        data = request.POST
        email = data['email_id']
        user = User.objects.create(email=email, username=email)
        user.first_name = data['name']
        user.save()
        profile = Profile.objects.get(user=user)
        sponser_id = Profile.objects.get(user_auto_id=data['refer_id'])
        placement_id = Profile.objects.get(user_auto_id=data['place_id'])
        profile.sponser_id = sponser_id.user
        profile.placement_id = placement_id.user
        if data['placement'] == 'left':
            profile.placement_position = 'L'
        else:
            profile.placement_position = 'R'
        profile.save()
        memeber = Members.objects.create(parent_id=placement_id.user, child_id=user)
        return HttpResponse('Success')

        # <QueryDict: {u'refer_id': [u'AVI3'], u'placement': [u'left'], u'name': [u'aTUL'], u'email_id': [u'JASVIN@GAMILI.COM'], u'country': [u'India'], u'place_id': [u'AVI3'], u'mob_number': [u'987456325121'], u'drptown': [u'ddELHIO']}
