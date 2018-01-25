from __future__ import unicode_literals
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.views.generic import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from forms import signup_form

from addons.accounts.models import Profile, Members, SupportTicket
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.models import Packages, User_packages

import sys
import hashlib
import random
import json

sys.path.append(settings.BASE_DIR)
from avicrypto import services
from lib.tree import load_users, find_min_max, is_member_of, is_parent_of

def index(request):
    context = {
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
    template = loader.get_template('website.html')
    return HttpResponse(template.render(context, request))

def bank_website(request):
    context = {}
    template = loader.get_template('avicrypto_bank.html')
    return HttpResponse(template.render(context, request))

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
                    associated_users = User.objects.filter(Q(email=data) | Q(username=data))
                    if associated_users.exists():
                        result = self.form_valid(form)
                        messages.success(request, 'User already exists')
                        return result
                    else:
                        user = User.objects.create(username=data_dict['email'], email=data_dict['email'], first_name=data_dict['first_name'], last_name=data_dict['last_name'])
                        user.set_password(str(data_dict['password']))
                        user.username = user.profile.user_auto_id
                        user.save()
                        update_profile(user, request.POST)
                        body = "Welcome to Avicrypto! "
                        services.send_email_mailgun('Welcome to Avicrypto', body, data_dict['email'], from_email="postmaster")
                        result = self.form_valid(form)
                        messages.success(request, 'An email has been sent to {0}. Please check its inbox to continue reseting password.'.format(data))
                        return result
                else:
                    result = self.form_valid(form)
                    messages.success(request, 'Not an email address.')
                    return result
            else:
                result = self.form_valid(form)
                messages.success(request, 'Data invalid.')
                return result
        except Exception as e:
            raise

        return self.form_invalid(form)

def login_fn(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            template = loader.get_template('login.html')
            if 'ref' not in request.GET:
                context = {
                    'referal': "",
                    'sponser_id': "",
                    'placement_user_left_id': "",
                    'placement_user_right_id': ""
                }
            else:
                referal = request.GET['ref']
                sponser = Profile.objects.get(my_referal_code=referal)
                sponser_id = sponser.user_auto_id
                placement_users = find_min_max(sponser.user)

                context = {
                    'referal': referal,
                    'sponser_id': sponser_id,
                    'placement_user_left_id': placement_users[0].profile.user_auto_id,
                    'placement_user_right_id': placement_users[1].profile.user_auto_id
                }
            return HttpResponse(template.render(context, request))

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse(json.dumps({"status": "ok"}))
                else:
                    return HttpResponse(json.dumps({
                        "status": "error",
                        "message": "Id id not active."            
                    }))
            else:
                return HttpResponse(json.dumps({
                    "status": "error",
                    "message": "Email or password is incorrect."            
                }))
    else:
        return HttpResponseRedirect('/home')

def check_referal(request):
    referal = request.GET['referal']
    if Profile.objects.filter(my_referal_code=referal).exists():
        sponser = Profile.objects.get(my_referal_code=referal)
        sponser_id = sponser.user_auto_id
        placement_users = find_min_max(sponser.user)

        response = {
            'status': 'ok',
            'data': {
                'referal': referal,
                'sponser_id': sponser_id,
                'placement_user_left_id': placement_users[0].profile.user_auto_id,
                'placement_user_right_id': placement_users[1].profile.user_auto_id
            }
        }

        return HttpResponse(json.dumps(response))
    else:
        return HttpResponse(json.dumps({
            'status': 'error',
            'message': 'Referal address invalid'
        }))

def check_placement(request):
    referal = request.GET['referal']
    sponcer_id = request.GET['sponcer_id']
    position = request.GET['position']

    if Profile.objects.filter(my_referal_code=referal).exists():
        sponser = Profile.objects.get(my_referal_code=referal)
        sponser_id = sponser.user_auto_id
        placement_users = find_min_max(sponser.user)

        response = {
            'status': 'ok',
            'data': {
                'referal': referal,
                'sponser_id': sponser_id,
                'placement_user_left_id': placement_users[0].profile.user_auto_id,
                'placement_user_right_id': placement_users[1].profile.user_auto_id
            }
        }

        return HttpResponse(json.dumps(response))
    else:
        return HttpResponse(json.dumps({
            'status': 'error',
            'message': 'Referal address invalid'
        }))

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
        packages = User_packages.objects.filter(user=user)
        support_tickets = SupportTicket.objects.filter(user=user)

        context = {
            'link': request.META['HTTP_HOST'] + '/login?ref=' + str(user.profile.my_referal_code),
            'packages': packages,
            'support_tickets': support_tickets,
            'support_tickets_choices': SupportTicket.status_choices
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
        country_json = json.load(open('country.json'))
        country = ""
        if user.profile.country:
            country = (item for item in country_json if item["country_code"] == user.profile.country).next()

        context = {
            'user_country': country,
            "countries": country_json
        }

        template = loader.get_template('profile.html')

        if not request.user.is_authenticated():
            return HttpResponseRedirect('/error')
        else:
            return HttpResponse(template.render(context, request))

    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        country = request.POST.get("country", "US")

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        user.profile.country = country
        user.profile.save()

        return HttpResponse(json.dumps({"status": "success"}))
    else:
        return HttpResponseRedirect('/error')

@login_required(login_url="/login")
@csrf_exempt
def support(request):
    if request.method == 'GET':
        template = loader.get_template('support.html')
        context = {
            'user': request.user
        }
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        description = request.POST.get("description", "")
        SupportTicket.objects.create(user=request.user, description=description, status="P")
        return HttpResponse(json.dumps({
            'status': 'ok',
            'message': 'Our support team will get back to you.'
        }))
        # services.support_mail('Support Ticket', request.POST.get("description", ""), 'harshulkaushik9@gmail.com', from_email="postmaster")
        # return HttpResponse('Mail sent to adminstrator', content_type="application/json")

@login_required(login_url="/login")
@csrf_exempt
def network(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('network.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        data = traverse_tree(request.user)
        return HttpResponse(data)

@login_required(login_url="/login")
def network_init(request):
    user = request.user
    data = traverse_tree(request.user)
    data = json.loads(data)
    # data['collapsed'] = True
    data['className'] = 'top-level'
    return HttpResponse(json.dumps(data))

@login_required(login_url="/login")
def network_parent(request):
    user = request.user
    data = traverse_tree(request.user)
    return HttpResponse(data)

@login_required(login_url="/login")
def network_children(request, user_id):
    print user_id
    user = User.objects.get(id=user_id)
    print user
    data = traverse_tree(user)
    data = json.loads(data)
    print data
    data = {
        'children': data['children']
    }
    return HttpResponse(json.dumps(data))


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
    profile.country = data.get('country', "US")
    profile.mobile = data.get('mobile', None)

    referal_code = data.get('referal', None)
    sponcer_id = data.get('sponcer_id', None)
    placement_id = data.get('placement_id', None)
    placement_position = data.get('placement_position', "L")

    if referal_code:
        sponser_user = Profile.objects.get(my_referal_code=referal_code)
        if sponser_user:
            placement_users = find_min_max(sponser_user.user)

            if placement_position == "L":
                profile.placement_id = placement_users[0]
            else:
                profile.placement_id = placement_users[1]

            profile.placement_position = placement_position
            profile.referal_code = referal_code
            profile.sponcer_id = sponser_user.user
            Members.objects.create(parent_id=profile.placement_id, child_id=user)

    profile.save()

def traverse_tree(user, level=4):
    ref_code = "/add/user?ref={}&place={}".format(user.profile.my_referal_code, user.profile.user_auto_id)
    data = load_users(user, ref_code, level=level)
    return json.dumps(data)

@csrf_exempt
def add_user(request):

    if request.method == 'GET':
        referal = request.GET.get('ref')
        sponser_id = Profile.objects.filter(my_referal_code=referal)
        sponser_id = sponser_id[0].user_auto_id
        pos = request.GET.get('pos', "left")
        placement_id = request.GET.get('parent_placement_id')

        context = {
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
        email = data['email']

        if not User.objects.filter(email=email).exists():
            user = User.objects.create(email=email, username=email)
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()

            profile = Profile.objects.get(user=user)
            sponser_id = Profile.objects.get(user_auto_id=data['sponser_id'])
            placement_id = Profile.objects.get(user_auto_id=data['placement_id'])
            profile.sponser_id = sponser_id.user
            profile.placement_id = placement_id.user
            profile.mobile = data['mobile']
            profile.country = data['country']
            token = get_token(email)
            profile.token = token

            if data['placement'] == 'left':
                profile.placement_position = 'L'
            else:
                profile.placement_position = 'R'

            profile.save()

            body = "Create password for your account: http://www.avicrypto.us/reset-password/" + profile.token
            services.send_email_mailgun('Welcome to Avicrypto', body, email, from_email="postmaster")

            Members.objects.create(parent_id=placement_id.user, child_id=user)
            message = "Success"
        else:
			message = "Email address already registered."

        return HttpResponse(message)

def get_token(data):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    if isinstance(data, unicode):
        data = data.encode('utf8')
    return hashlib.sha1(salt + data).hexdigest()

def reset_password(request, token):
	if request.method == "POST":
		password = request.POST.get('password', '')
		profile = get_object_or_404(Profile, token=token)

		profile.user.set_password(password)
		profile.token = ""

		profile.save()
		profile.user.save()
		content = {
			"message": "Password has been successfully changed."
		}
		return render(request, 'reset-password.html', content)
	else:
		profile = get_object_or_404(Profile, token=token)
		return render(request, 'reset-password.html')