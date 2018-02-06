import requests
from django.contrib.auth.decorators import user_passes_test

uri = 'https://api.mailgun.net/v3/avicrypto.us/messages'
key = 'key-1055741f06d43a548bf5def6962b536a'

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