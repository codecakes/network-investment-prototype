"""
This is being used in tree.py
"""


from addons.accounts.models import Profile, Members, User
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.models import Packages, User_packages

from django.db.models import Sum
from django.conf import settings
from django.db.models import Q


def lower_encode(member, leg_list):
    if type(member) == Members:
        val = str.lower(
            member.child_id.profile.placement_position.encode("utf-8"))
    elif type(member) == User and member.profile.placement_position:
        val = str.lower(member.profile.placement_position.encode("utf-8"))
    else:
        return None
    return val in leg_list


def find_left(member1, member2):
    return member1 if lower_encode(member1, ('l', 'left')) else member2

def find_right(member1, member2):
    return member1 if lower_encode(member1, ('r', 'right')) else member2


def is_left(member):
    return lower_encode(member, ('l', 'left'))


def is_right(member):
    return lower_encode(member, ('r', 'right'))

LEG = {'l': is_left, 'r': is_right}

def get_left(user):
    """Helper Function: Gets left node of user node"""
    members = Members.objects.filter(parent_id=user.id)
    assert len(members) <= 2

    if len(members) == 0:
        return None
    if len(members) > 1:
        res = find_left(*members)
        child_member = res.child_id
    elif is_left(members[0]):
        child_member = members[0].child_id
    else:
        child_member = None
    return child_member


def get_right(user):
    """Helper Function: Gets right node of user node"""
    members = Members.objects.filter(parent_id=user.id)
    assert len(members) <= 2

    if len(members) == 0:
        return None
    if len(members) > 1:
        res = find_right(*members)
        child_member = res.child_id
    elif is_right(members[0]):
        child_member = members[0].child_id
    else:
        child_member = None
    return child_member


def get_package(user):
    packages = User_packages.objects.filter(user=user, status='A')
    if packages:
        # packages = User_packages.objects.get(user=user, status='A')
        return packages[0] if packages else None
    return None


def calc_txns_reducer(txn_obj):
    # import pdb
    # pdb.set_trace()
    if type(txn_obj) == float:
        return txn_obj
    if txn_obj:
        if txn_obj[0]:
            return txn_obj[0].data_sum
    # if txn_obj.values():
    #     if txn_obj.values()[0]['data_sum']:
    #         return txn_obj.values()[0]['data_sum']
    return 0.0

######## calculate binary/direct/roi txns per user ########### 

# TODO: cache that decorator!
def binary_txns(user, start_dt, end_dt, **kw):
    # get avicrypto wallet
    avicrypto_user = kw.get('admin', User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us'))
    avicrypto_wallet = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'AW')
    # avicrypto_wallet =  avicrypto_wallet[0] if avicrypto_wallet else Wallet.objects.create(owner = avicrypto_user, wallet_type = 'AW')

    # get user wallet
    pkg = get_package(user)
    user_BN_wallet = Wallet.objects.filter(owner = user, wallet_type = 'BN')
    # user_BN_wallet = user_BN_wallet[0] if user_BN_wallet else Wallet.objects.create(owner = user, wallet_type = 'BN')

    subquery = Q(reciever_wallet__in=user_BN_wallet) & Q(status__in=['C', 'processing', 'paid']) # & Q(sender_wallet__in=avicrypto_wallet) 
    return calc_txns_reducer(Transactions.objects.filter(subquery, tx_type="binary", created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount')))

def direct_txns(user, start_dt, end_dt, **kw):
    # get avicrypto wallet
    avicrypto_user = kw.get('admin', User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us'))
    avicrypto_wallet = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'AW')
    
    # get user wallet
    pkg = get_package(user)
    user_DR_wallet = Wallet.objects.filter(owner = user, wallet_type = 'DR')
    
    subquery = Q(reciever_wallet__in=user_DR_wallet) & Q(status__in=['C', 'processing', 'paid']) # Q(sender_wallet__in=avicrypto_wallet) & 
    return calc_txns_reducer(Transactions.objects.filter(subquery, tx_type="direct", created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount')))


def roi_txns(user, start_dt, end_dt, **kw):
    # get avicrypto wallet
    avicrypto_user = kw.get('admin', User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us'))
    avicrypto_wallet = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'AW')
    avicrypto_wallet =  avicrypto_wallet[0] if avicrypto_wallet else Wallet.objects.create(owner = avicrypto_user, wallet_type = 'AW')

    # get user wallet
    pkg = get_package(user)
    user_ROI_wallet = Wallet.objects.filter(owner = user, wallet_type = 'ROI')
    
    subquery = Q(reciever_wallet__in=user_ROI_wallet) & Q(status__in=['C', 'processing', 'paid']) # Q(sender_wallet__in=avicrypto_wallet) & 
    return calc_txns_reducer(Transactions.objects.filter(subquery, tx_type="roi", created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount')))


def direct_child(user, start_dt, end_dt, leg = 'l'):
    # get avicrypto wallet
    avicrypto_user = User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us')
    avicrypto_wallet = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'AW')
    
    check_leg = LEG[leg]
    child_user = get_left(user) if leg == 'l' else get_right(user) 
    # get user wallet
    if child_user and check_leg(child_user):
        pkg = get_package(child_user)
        user_DR_wallet = Wallet.objects.filter(owner = child_user, wallet_type = 'DR')
        
        subquery = Q(reciever_wallet__in=user_DR_wallet) & Q(status__in=['C', 'processing', 'paid'])
        return calc_txns_reducer(Transactions.objects.filter(subquery, tx_type="direct", created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount')))
    return None

def binary_child(user, start_dt, end_dt, leg = 'l'):
    # get avicrypto wallet
    avicrypto_user = User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us')
    avicrypto_wallet = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'AW')
    
    check_leg = LEG[leg]
    child_user = get_left(user) if leg == 'l' else get_right(user) 
    # get user wallet
    if child_user and check_leg(child_user):
        pkg = get_package(child_user)
        user_BN_wallet = Wallet.objects.filter(owner = child_user, wallet_type = 'BN')
        
        subquery = Q(reciever_wallet__in=user_BN_wallet) & Q(status__in=['C', 'processing', 'paid'])
        return calc_txns_reducer(Transactions.objects.filter(subquery, tx_type="binary", created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount')))
    return None