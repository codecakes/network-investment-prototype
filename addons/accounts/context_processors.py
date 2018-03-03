from addons.packages.models import Packages, User_packages

def notification(request):
    user = request.user

    if user.is_authenticated():

        enable_notification = False
        notification_count = 0

        email_verified = user.profile.email_verified

        if not email_verified:
            notification_count += 1

        has_package = User_packages.objects.filter(status='A', user=user).exists()
        if not has_package:
            notification_count += 1

        has_crypto_account = True
        has_btc = True if user.useraccount.btc_address and user.useraccount.btc_address != 'None' else False
        has_eth = True if user.useraccount.eth_address and user.useraccount.eth_address != 'None' else False
        has_xrp = True if (user.useraccount.xrp_address and user.useraccount.xrp_destination_tag and user.useraccount.xrp_address != 'None' and user.useraccount.xrp_destination_tag != 'None') else False

        if has_btc or has_eth or has_xrp:
            has_crypto_account = True
        else:
            has_crypto_account = False
            notification_count += 1

        if notification_count > 0:
            enable_notification = True

        return {
            'enable_notification': enable_notification,
            'notification_count': notification_count,
            'email_verified': email_verified,
            'has_packages': has_package,
            'has_crypto_account': has_crypto_account,
        }
    else:
        return {}
