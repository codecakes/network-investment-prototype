import requests
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from addons.accounts.models import *
from addons.packages.models import *

uri = 'https://api.mailgun.net/v3/avicrypto.us/messages'
key = 'key-1055741f06d43a548bf5def6962b536a'

def send_email_results(amt, crypto_addr, bool_result):
    """
    @params:
        crypto_addr: XRP/BTC/ETH address of a user
        bool_result: True or False.

    Write a function that :
    1. Finds the user email based on their `crypto_addr` which could be anyone of XRP/ETH/BTC. 
    2. Sends them an email telling them if their transaction was successful or not.
    3. If it was successful then set their package to active for the price `amt`
    else tell their transaction failed.
    """
    user = UserAccount.objects.get(Q(btc_address=crypto_addr) | Q(xrp_address=crypto_addr) | Q(eth_address=crypto_addr)).user
    email_data = {
        full_name:user.first_name+' '+user.last_name
    }
    if bool_result:
        body = render_to_string('mail/transaction_success.html', email_data)
        package = Packages.objects.get(price=amt)
        set_package_status(user, package, 'A')
        send_email_mailgun('AVI Crypto Transaction Success', body, user.email, from_email="postmaster")
    else:
        body = render_to_string('mail/transaction_failed.html', email_data)
        send_email_mailgun('AVI Crypto Transaction Failed', body, user_email, from_email="postmaster")
    pass

def send_email_mailgun(subject, body, receipient_emails, from_email="postmaster"):
    data = {
        "from": "AviCrypto <mail@avicrypto.us>",
        "to": receipient_emails,
        "subject": subject,
        "html": body
    }
    return requests.post(uri, auth=("api", key), data=data)

def support_mail(subject, body, receipient_emails, from_email="postmaster"):
    data = {
        "from": "AviCrypto <mail@avicrypto.us>",
        "to": receipient_emails,
        "subject": subject,
        "html": body
    }

    return requests.post(uri, auth=("api", key), data=data)


# def crypto_account(function):
#     def wrapper(request, **kw):  
#         user = request.user  
#         if user and (user.useraccount.btc_address or user.useraccount.eth_address or (user.useraccount.xrp_address and user.useraccount.destination_tag)):
#             kw['package_access_disable'] = False
#         return function(request, **kw)
#     return wrapper

def active_required(function):
    dec = user_passes_test(lambda u: u.is_active, '/not-active', '')
    return dec(function)


def set_package_status(user, package, status):
    set_package = User_packages.objects.save(user=user, package=package, status=status)
    return True