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
        if not user.useraccount.btc_address or not user.useraccount.eth_address or not (user.useraccount.xrp_address and user.useraccount.xrp_destination_tag):
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
