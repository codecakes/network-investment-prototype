from __future__ import unicode_literals

import hashlib
import json
import random
import re
import sys
import datetime
from pytz import UTC
import calendar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import Context, RequestContext, loader
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import *
from django.core.exceptions import ObjectDoesNotExist
from addons.accounts.models import Members, Profile, SupportTicket, UserAccount
from addons.packages.lib.payout import (UTC, calc, calculate_investment,
                                        find_next_monday)
from addons.packages.models import Packages, User_packages
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from avicrypto import services
from lib.tree import (find_min_max, has_child, is_member_of, is_parent_of,
                      is_valid_leg, load_users)
from addons.accounts.lib.blockexplorer import validate_transaction

sys.path.append(settings.BASE_DIR)


def app_404(request):
    return render(request, '404.html')

def notactive(request):
    return HttpResponse("User is not active")

def traverse_tree(user, level=4):
    ref_code = "/add/user?ref={}&place={}".format(
        user.profile.my_referal_code, user.profile.user_auto_id)
    data = load_users(user, ref_code, level=level)
    return json.dumps(data)


def get_token(data):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    if isinstance(data, unicode):
        data = data.encode('utf8')
    return hashlib.sha1(salt + data).hexdigest()


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


def app_login(request):
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
            username = str(request.POST.get('username'))
            password = str(request.POST.get('password'))

            if username and password:
                if User.objects.filter(username=username).exists():
                    if User.objects.filter(username=username, is_active=True).exists():
                        user = authenticate(
                            username=username, password=password)
                        if user is not None:
                            login(request, user)
                            return HttpResponse(json.dumps({
                                "status": "ok",
                                "crypto_account": crypto_account_exists(user)
                            }))
                        else:
                            return HttpResponse(json.dumps({
                                "status": "error",
                                "message": "Username or password is incorrect."
                            }))
                    else:
                        return HttpResponse(json.dumps({
                            "status": "error",
                            "message": "Email address is not active."
                        }))
                else:
                    return HttpResponse(json.dumps({
                        "status": "error",
                        "message": "Invalid username."
                    }))
            else:
                return HttpResponse(json.dumps({
                    "status": "error",
                    "message": "Provide username or password."
                }))
    else:
        return HttpResponseRedirect('/home')


def app_signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        data = request.POST
        referal_code = data.get('referal', None)
        sponcer_id = data.get('sponcer_id', None)
        placement_id = data.get('placement_id', None)
        placement_position = data.get('placement_position', "L")

        if email and validate_email(email) == None:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            mobile = request.POST.get('mobile')
            password = request.POST.get('password')

            if re.match(r'^\+?1?\d{9,15}$', mobile):
                if not User.objects.filter(email=email).exists():

                    if referal_code:
                        try:
                            referal_user = Profile.objects.get(
                                my_referal_code=referal_code)
                            if placement_id:
                                placement_user_profile = Profile.objects.get(
                                    user_auto_id=placement_id)
                                placement_user = placement_user_profile.user

                                position = 'l' if 'L' == position else 'r'

                                if is_member_of(referal_user, placement_user):
                                    if has_child(placement_user, position):
                                        return HttpResponse(json.dumps({
                                            "status": "error",
                                            "message": "Placement user selected position is not empty."
                                        }))
                                else:
                                    return HttpResponse(json.dumps({
                                        "status": "error",
                                        "message": "Placement id user does not belong to the referal user."
                                    }))

                        except Profile.DoesNotExist:
                            content = {
                                "status": "error",
                                "message": "Referal code does not exist."
                            }
                            return HttpResponse(json.dumps(content))

                    user = User.objects.create(
                        username=email, email=email, first_name=first_name, last_name=last_name, is_active=False)
                    user.username = user.profile.user_auto_id
                    user.set_password(str(password))
                    user.save()

                    token = update_signup_user_profile(user, request.POST)

                    email_data = {
                        "user": user,
                        "token": token
                    }
                    body = render_to_string('mail/welcome.html', email_data)
                    services.send_email_mailgun(
                        'Welcome to Avicrypto', body, email, from_email="postmaster")

                    content = {
                        "status": "ok",
                        "message": "Thank you for registration. Soon you will receive a confirmation mail."
                    }
                    return HttpResponse(json.dumps(content))
                else:
                    content = {
                        "status": "error",
                        "message": "Email address already exist."
                    }
                    return HttpResponse(json.dumps(content))
            else:
                content = {
                    "status": "error",
                    "message": "Invalid mobile number."
                }
                return HttpResponse(json.dumps(content))
        else:
            content = {
                "status": "error",
                "message": "Not and email address."
            }
            return HttpResponse(json.dumps(content))


@login_required(login_url="/login")
def app_logout(request):
    logout(request)
    response = HttpResponseRedirect('/')
    return response


def app_activate_account(request, token):
    profile = get_object_or_404(Profile, token=token, user__is_active=False)
    profile.user.is_active = True
    profile.user.save()

    if profile.user.has_usable_password():
        profile.token = ""
        profile.save()
        return HttpResponseRedirect("/login")
    else:
        return HttpResponseRedirect("/reset-password/" + profile.token)


def app_forgot_password(request):
    content = {}
    if request.method == 'POST':
        email = request.POST.get("email", "")

        try:
            user = User.objects.get(email=email)
            token = get_token(user.username)
            email_data = {
                "token": token,
                "user": user
            }
            body = render_to_string('mail/reset-password.html', email_data)
            services.send_email_mailgun(
                'Reset Password Avicrypto', body, email, from_email="postmaster")
            content = {
                "status": "ok",
                "message": "Email has send to your address."
            }

            user.profile.token = token
            user.profile.save()

            return HttpResponse(json.dumps(content))
        except User.DoesNotExist:
            content = {
                "status": "error",
                "message": "Can't find that email, sorry."
            }
            return HttpResponse(json.dumps(content))

    return render(request, 'forgot-password.html', content)


def app_reset_password(request, token):
    if request.method == "POST":
        password = request.POST.get('password', '')
        profile = get_object_or_404(Profile, token=token, user__is_active=True)

        profile.user.set_password(password)
        profile.token = ""

        profile.save()
        profile.user.save()
        content = {
            "status": "ok",
            "message": "Password has been successfully changed."
        }
        return render(request, 'reset-password.html', content)
    else:
        profile = get_object_or_404(Profile, token=token, user__is_active=True)
        return render(request, 'reset-password.html')


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
    placement_id = request.GET['placement_id']
    position = request.GET['position']

    position = 'l' if 'left' == position else 'r'

    if Profile.objects.filter(my_referal_code=referal).exists():
        if Profile.objects.filter(user_auto_id=placement_id).exists():
            referal_user = Profile.objects.get(my_referal_code=referal).user
            placement_user = Profile.objects.get(
                user_auto_id=placement_id).user

            if is_member_of(referal_user, placement_user):
                if not has_child(placement_user, position):
                    return HttpResponse(json.dumps({
                        "status": "ok"
                    }))
                else:
                    return HttpResponse(json.dumps({
                        "status": "error",
                        "message": "Placement user selected position is not empty."
                    }))
            else:
                return HttpResponse(json.dumps({
                    "status": "error",
                    "message": "Placement id user does not belong to the referal user."
                }))
        else:
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': 'Invalid placement id'
            }))
    else:
        return HttpResponse(json.dumps({
            'status': 'error',
            'message': 'Referal address invalid'
        }))


def error(request):
    template = loader.get_template('error.html')
    context = {
        'user': 'None'
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login")
def home(request):

    if request.method == 'GET':
        user = request.user
        today = UTC.normalize(UTC.localize(datetime.datetime.utcnow()))
        is_day = calendar.weekday(today.year, today.month, today.day)
        if today.hour == 23 and today.minute == 59 and is_day == 6:
            calculate_investment(user)

        packages = User_packages.objects.filter(user=user)
        support_tickets = SupportTicket.objects.filter(user=user)

        context = {
            'link': request.META['HTTP_HOST'] + '/login?ref=' + str(user.profile.my_referal_code),
            'packages': packages,
            'support_tickets': support_tickets,
            'support_tickets_choices': SupportTicket.status_choices,
            'enable_withdraw': False,
            'crypto_account':crypto_account_exists(request.user),
            'package_status':has_package(request.user),
            'wallet_type_choices': Wallet.wallet_type_choice
        }

        if 0<= is_day < 2:
            context["enable_withdraw"] = True

        user_active_package = [
            package for package in packages if package.status == 'A']
        if user_active_package:
            pkg = user_active_package[0]
            dt = UTC.normalize(UTC.localize(
                datetime.datetime.now())) - pkg.created_at
            context["payout_remain"] = pkg.package.no_payout - (dt.days/7)
            next_payout = find_next_monday()
            context["next_payout"] = "%s-%s-%s" % (
                next_payout.year, next_payout.month, next_payout.day)

        if len(user_active_package) == 0:
            context["weekly_payout"] = 0
            context["direct_payout"] = 0
            context["binary_payout"] = 0
            context["user_active_package_value"] = 0
        else:
            context["weekly_payout"] = user_active_package[0].weekly
            context["direct_payout"] = user_active_package[0].direct
            context["binary_payout"] = user_active_package[0].binary
            context["user_active_package_value"] = user_active_package[0].package.price

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
            country = (
                item for item in country_json if item["country_code"] == user.profile.country).next()

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
        btc_address = request.POST.get("btc_address")
        eth_address = request.POST.get("eth_address")
        xrp_address = request.POST.get("xrp_address")
        destination_tag = request.POST.get("destination_tag")
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        user.profile.country = country
        user.profile.save()
        try:
            user.useraccount.btc_address = btc_address
            user.useraccount.eth_address = eth_address
            user.useraccount.xrp_address = xrp_address
            user.useraccount.eth_destination_tag = destination_tag
            user.useraccount.save()
        except ObjectDoesNotExist:
            user_account = UserAccount.objects.create(user=user)
            user_account.btc_address = btc_address
            user_account.eth_address = eth_address
            user_account.xrp_address = xrp_address
            user_account.eth_destination_tag = destination_tag

            if btc_address:
                Wallet.objects.create(user=user, wallet_type="BTC")
            
            if eth_address:
                Wallet.objects.create(user=user, wallet_type="ETH")

            if xrp_address:
                Wallet.objects.create(user=user, wallet_type="XRP")

            user_account.save()
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
        SupportTicket.objects.create(
            user=request.user, description=description, status="P")
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
        context = {"package_access_disable":True,'package_status':has_package(request.user)}
        user = request.user
        if user and (user.useraccount.btc_address or user.useraccount.eth_address or (user.useraccount.xrp_address and user.useraccount.eth_destination_tag)):
            context["package_access_disable"] = False
        template = loader.get_template('network.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        data = traverse_tree(request.user)
        return HttpResponse(data)


@login_required(login_url="/login")
def network_init(request):
    user = request.user
    data = traverse_tree(user)
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
    user = User.objects.get(id=user_id)
    data = traverse_tree(user)
    data = json.loads(data)
    data = {
        'children': data['children']
    }
    return HttpResponse(json.dumps(data))


def simple_upload(request):
    if request.method == 'POST' and request.FILES['passfront'] and request.FILES['passback'] and request.FILES['passphoto']:
        passfront = request.FILES['passfront']
        passback = request.FILES['passback']
        passphoto = request.FILES['passphoto']
        fs = FileSystemStorage()
        filename_passfront = fs.save(passfront.name, passfront)
        filename_passback = fs.save(passback.name, passback)
        filename_passphoto = fs.save(passphoto.name, passphoto)
        uploaded_file_url = fs.url(filename_passfront) or fs.url(
            filename_passback) or fs.url(filename_passphoto)
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

# TODO: This is for signup purposes only. Refactor
def update_signup_user_profile(user, data):
    profile = Profile.objects.get(user=user)
    profile.country = data.get('country', "US")
    profile.mobile = data.get('mobile', None)
    referal_code = data.get('referal', None)
    sponcer_id = data.get('sponcer_id', None)
    placement_id = data.get('placement_id', None)
    placement_position = data.get('placement_position', "L")
    token = get_token(user.username)
    profile.token = token

    if referal_code:
        sponser_user = Profile.objects.get(my_referal_code=referal_code)

        if placement_id:
            profile.placement_id = Profile.objects.get(
                user_auto_id=placement_id).user
        else:
            placement_users = find_min_max(sponser_user.user)

            if placement_position == "R":
                profile.placement_id = placement_users[1]
            else:
                profile.placement_id = placement_users[0]

        profile.placement_position = placement_position
        profile.referal_code = referal_code
        profile.sponcer_id = sponser_user.user
        Members.objects.create(parent_id=profile.placement_id, child_id=user)
    profile.save()

    return token

@login_required(login_url="/login")
def update_user_profile(user, data):
    profile = Profile.objects.get(user=user)
    profile.country = data.get('country', "US")
    profile.mobile = data.get('mobile', None)

    referal_code = data.get('referal', None)
    sponcer_id = data.get('sponcer_id', None)
    placement_id = data.get('placement_id', None)
    placement_position = data.get('placement_position', "L")
    token = get_token(user.username)

    profile.token = token

    if referal_code:
        sponser_user = Profile.objects.get(my_referal_code=referal_code)

        if placement_id:
            profile.placement_id = Profile.objects.get(
                user_auto_id=placement_id).user
        else:
            placement_users = find_min_max(sponser_user.user)

            if placement_position == "R":
                profile.placement_id = placement_users[1]
            else:
                profile.placement_id = placement_users[0]

        profile.placement_position = placement_position
        profile.referal_code = referal_code
        profile.sponcer_id = sponser_user.user
        Members.objects.create(parent_id=profile.placement_id, child_id=user)

    profile.save()

    return token


@login_required(login_url="/login")
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
            placement_id = Profile.objects.get(
                user_auto_id=data['placement_id'])
            if placement_id.user.is_active == False:
                content = {
                    "status": "error",
                    "message": "placement user is not active",
                }
                return HttpResponse(json.dumps(content))
            user = User.objects.create(email=email, username=email)
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.username = user.profile.user_auto_id
            user.is_active = False
            user.save()

            profile = Profile.objects.get(user=user)
            sponser_id = Profile.objects.get(user_auto_id=data['sponser_id'])
            
            # check user active or not 
            profile.sponser_id = sponser_id.user
            profile.placement_id = placement_id.user
            profile.mobile = data['mobile']
            profile.country = data['country']
            token = get_token(user.username)
            profile.token = token

            if data['placement'] == 'left':
                profile.placement_position = 'L'
            else:
                profile.placement_position = 'R'

            profile.save()

            # body = "Create password for your account: http://www.avicrypto.us/reset-password/" + profile.token
            # services.send_email_mailgun('Welcome to Avicrypto', body, email, from_email="postmaster")

            email_data = {
                "user": user,
                "token": token
            }
            body = render_to_string('mail/welcome.html', email_data)
            services.send_email_mailgun(
                'Welcome to Avicrypto', body, email, from_email="postmaster")

            Members.objects.create(parent_id=placement_id.user, child_id=user)
            content = {
                "status": "ok",
                "message": "Registration complete.",
            }
        else:
            content = {
                "status": "ok",
                "message": "Email address already registered.",
            }

        return HttpResponse(json.dumps(content))

def crypto_account_exists(user):
    try:
        if user and (user.useraccount.btc_address or user.useraccount.eth_address or (user.useraccount.xrp_address and user.useraccount.eth_destination_tag)):
            return True
        else:
            return  False
    except ObjectDoesNotExist:
        user_account = UserAccount.objects.create(user=user)
        if user and (user.useraccount.btc_address or user.useraccount.eth_address or (user.useraccount.xrp_address and user.useraccount.eth_destination_tag)):
            return True
        else:
            return False

@login_required(login_url="/login")
def validate_user_transaction(request):
    if request.method == "POST":
        amount = request.POST.get("amount", 0)
        source_address = request.POST.get("source_address", "")
        address = request.POST.get("address", "")
        txn_id = request.POST.get("txn_id", "")
        coin = request.POST.get("coin", "btc")
        destination_tag = request.POST.get("destination_tag", "btc")

        validate_transaction(amount, source_address, address, txn_id, coin.lower())

        return HttpResponse(json.dumps({
            "status": "ok",
            "message": "We will send a conformation email, whether the transaction is valid or not."
        }))

def has_package(user):    
    pkg = User_packages.objects.filter(status='A', user = user)
    return True if pkg else False

@login_required(login_url="/login")
def withdraw(request):
    if request.method == "POST":
        user = request.user
        currency_type = request.POST.get('currency', "")
        if currency_type:
            user_account = UserAccount.objects.filter(user=user)
            owner = User.objects.get(id=1)
            if user_account:
                user_account = user_account[0]
                if currency_type == "BTC":
                    if not user_account.btc_address or user_account.btc_address == "None":
                        return HttpResponse(json.dumps({
                            "status": "error",
                            "message": "Add selected crypto currency account first."
                        }))
                    else:
                        crypto_addr = user_account.btc_address
                elif currency_type == "XRP":
                    if not user_account.xrp_address or user_account.xrp_address == "None":
                        return HttpResponse(json.dumps({
                            "status": "error",
                            "message": "Add selected crypto currency account first."
                        }))
                    else:
                        crypto_addr = user_account.xrp_address
                elif currency_type == "ETH":
                    if not user_account.eth_address or user_account.eth_address == "None":
                        return HttpResponse(json.dumps({
                            "status": "error",
                            "message": "Add selected crypto currency account first."
                        }))
                    else:
                        crypto_addr = user_account.eth_address

                if not Wallet.objects.filter(owner=owner, wallet_type=currency_type).exists():
                    owner_wallet = Wallet.objects.create(owner=owner, wallet_type=currency_type)
                else:
                    owner_wallet = Wallet.objects.get(owner=owner, wallet_type=currency_type)

                if not Wallet.objects.filter(owner=user, wallet_type=currency_type).exists():
                    user_wallet = Wallet.objects.create(owner=user, wallet_type=currency_type)
                else:
                    user_wallet = Wallet.objects.get(owner=user, wallet_type=currency_type)

                user_packages = User_packages.objects.get(user=user)

                if user_packages.total_payout > 0:
                    total_payout = user_packages.total_payout
                    owner_amount = total_payout / 10
                    user_amount = total_payout - owner_amount

                    transaction = Transactions.objects.create(sender_wallet=owner_wallet, reciever_wallet=user_wallet, amount=user_amount)

                    owner_wallet.amount = owner_wallet.amount + owner_amount
                    owner_wallet.save()

                    user_wallet.amount = 0
                    user_wallet.save()

                    user_packages.total_payout = 0
                    user_packages.save()

                    services.send_email_mailgun('AVI Crypto Transaction Success', "Your withdrawal is successful, your transaction is pending. Your transaction is settled within 48 hours in your chosen account.", user.email, from_email="postmaster")

                    email_data = {
                        "user": user,
                        "owner_amount": owner_amount,
                        "user_amount": user_amount,
                        "total_payout": total_payout,
                        "currency_type": currency_type,
                        "transaction": transaction,
                        "today": UTC.normalize(UTC.localize(datetime.datetime.utcnow()))
                    }
                    body = render_to_string('mail/welcome.html', email_data)
                    services.send_email_mailgun('AVI Crypto Transaction Success', body, "admin@avicrypto.us", from_email="postmaster")

                    return HttpResponse(json.dumps({
                        "status": "ok",
                        "message": "Your withdrawal is successful, your transaction is pending. Your transaction is settled within 48 hours in your chosen account."
                    }))
                else:
                    return HttpResponse(json.dumps({
                        "status": "error",
                        "message": "Amount is zero."
                    }))
            else:
                return HttpResponse(json.dumps({
                    "status": "error",
                    "message": "Add crypto account address."
                }))
        else:
            return HttpResponse(json.dumps({
                "status": "error",
                "message": "Select currency for withdraw."
            }))