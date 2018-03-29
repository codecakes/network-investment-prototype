from addons.accounts.models import User, Members, Profile
from addons.packages.models import Packages, User_packages
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer, get_left, get_right
from django.conf import settings
from django.db.models import Count, Min, Sum, Avg
import pytz
import calendar
from datetime import datetime, timedelta, date
from functools import wraps
from avicrypto.lib.dsm import StateMachine

from django.db.models import Q

from payout_helpers.helpers import find_next_monday
from payout_helpers.payout_aux import get_package
from payout_helpers.weekly import weekly_wet, calc_weekly
from payout_helpers.direct import direct_wet, calc_direct
from payout_helpers.binary import binary_wet, calc_binary


UTC = pytz.UTC

EPOCH_BEGIN = START_TIME = getattr(settings, 'EPOCH_BEGIN', UTC.normalize(
    UTC.localize(datetime(2017, 12, 1, 00, 00, 00))))

# TODO: Lotsa caching decorators


# def filter_by_leg_user(member, leg):
#     """return only members of `leg`"""
#     u = get_user_from_member(member)
#     return LEG[leg](u)


# def traverse_members(filtered_members, sponsor_id, last_date, next_date):
#     # tree level traversal - get more members per child level
#     # child_members = map(get_user_from_member, filtered_members)
#     child_members = reduce(lambda x, y: x | y, [Members.objects.filter(
#         parent_id=m.child_id) for m in filtered_members])
#     # filter paying sponsored members
#     child_members = filter_by_sponsor(
#         sponsor_id, last_date, next_date, child_members)
#     if len(child_members):
#         #print "child_members is", child_members
#         # res = traverse_members(child_members, sponsor_id, last_date, next_date)
#         # print "traverse_members is ", res
#         return filtered_members + traverse_members(child_members, sponsor_id, last_date, next_date)
#     else:
#         return []




# ############## Calculate Investment ###################
INVESTMENT_TYPE = {
    'weekly_wet': weekly_wet,
    'direct_wet': direct_wet,
    'binary_wet': binary_wet,
    'direct': calc_direct,
    'binary': calc_binary,
    'weekly': calc_weekly
    # 'daily': calc_daily
}


def calc(user, last_date, investment_type):
    """
    investment_tytepe: can be direct, binary, weekly payouts
    Then set last_date = next_date
    """
    next_date = find_next_monday()
    return INVESTMENT_TYPE[investment_type](user, last_date, next_date)


def calc_txns_reducer(txn_obj):
    if type(txn_obj) == float:
        return txn_obj
    return txn_obj.data_sum


def calc_txns(start_dt, end_dt, **kw):
    """
    Calculates total payout between date ranges
    """
    import pdb
    pdb.pprint.pprint(kw, depth=2)

    # assert Transactions.objects.all()
    sum_subquery = Q(reciever_wallet__in=[
        kw['user_ROI_wallet'], 
        kw['user_DR_wallet'],
        kw['user_BN_wallet'] 
        ], status="C") & Q(tx_type__in=["roi", "direct", "binary"])
    sum_txns = Transactions.objects.filter(sum_subquery, created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount'))
    

    diff_subquery = Q(reciever_wallet__in=[
        kw['user_btc'],
        kw['user_eth'],
        kw['user_xrp']
        ]) & Q(tx_type__in=["W", "U", "topup"]) #status__in=["pending", "processing", "C", "paid"])
    # deduct withdrawals from all wallet types
    diff_txns = Transactions.objects.filter(diff_subquery, created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount'))
    # pdb.set_trace()
    # return sum_txns - diff_txns
    if sum_txns:
        agg = reduce(lambda x, y: calc_txns_reducer(x) + calc_txns_reducer(y), sum_txns)
        agg = agg if type(agg) == float else agg.data_sum
    else:
        agg = 0.0
    
    if diff_txns:
        diff = reduce(lambda x, y: calc_txns_reducer(x) + calc_txns_reducer(y),  diff_txns)    
        diff = diff if type(diff) == float else diff.data_sum
    else:
        diff = 0.0
    print "agg: %s | diff: %s | agg-diff=%s " %(agg, diff, agg - diff if diff_txns else agg)
    return agg - diff


def update_wallet_dt(user, wallet, wallet_type, last_date):
    # wallet, _ = Wallet.objects.get_or_create(owner=user, wallet_type=wallet_type)
    wallet = wallet.first() if wallet else Wallet.objects.create(owner=user, wallet_type=wallet_type)
    p = Profile.objects.get(user=user)
    wallet.created_at = p.created_at if wallet.created_at > p.created_at else wallet.created_at
    wallet.save(update_fields=['created_at'])
    return wallet

def check_pkg_investment(func):
    @wraps(func)
    def wrapped_f(*args, **kw):
        user, pkg, last_date, next_payout = args
        if pkg:
            return func(*args, **kw)
        return
    return wrapped_f


@check_pkg_investment
def run_investment_calc(user, pkg, last_date, next_payout, **admin_param):
    # get user and avicrypto wallets
    user_btc = Wallet.objects.filter(owner=user, wallet_type='BTC')
    user_btc = update_wallet_dt(user, user_btc, 'BTC', last_date)
    
    user_eth = Wallet.objects.filter(owner=user, wallet_type='ETH')
    user_eth = update_wallet_dt(user, user_eth, 'ETH', last_date)

    user_xrp = Wallet.objects.filter(owner=user, wallet_type='XRP')
    user_xrp = update_wallet_dt(user, user_xrp, 'XRP', last_date)

    user_ROI_wallet = Wallet.objects.filter(owner=user, wallet_type='ROI')
    user_ROI_wallet = update_wallet_dt(user, user_ROI_wallet, 'ROI', last_date)

    user_DR_wallet = Wallet.objects.filter(owner=user, wallet_type='DR')
    user_DR_wallet = update_wallet_dt(user, user_DR_wallet, 'DR', last_date)

    user_BN_wallet = Wallet.objects.filter(owner=user, wallet_type='BN')
    user_BN_wallet = update_wallet_dt(user, user_BN_wallet, 'BN', last_date)

    # avicrypto_user = User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us')
    avicrypto_user = admin_param.get('admin', User.objects.get(
        username='harshul', email='harshul.kaushik@avicrypto.us'))
    avicrypto_wallet = Wallet.objects.filter(
        owner=avicrypto_user, wallet_type='AW')
    avicrypto_wallet = update_wallet_dt(avicrypto_user, avicrypto_wallet, 'AW', last_date)

    avicrypto_btc = Wallet.objects.filter(
        owner=avicrypto_user, wallet_type='BTC')
    avicrypto_btc = update_wallet_dt(avicrypto_user, avicrypto_btc, 'BTC', last_date)

    avicrypto_eth = Wallet.objects.filter(
        owner=avicrypto_user, wallet_type='ETH')
    avicrypto_eth = update_wallet_dt(avicrypto_user, avicrypto_eth, 'ETH', last_date)

    avicrypto_xrp = Wallet.objects.filter(
        owner=avicrypto_user, wallet_type='XRP')
    avicrypto_xrp = update_wallet_dt(avicrypto_user, avicrypto_xrp, 'XRP', last_date)

    ################# Calculations Happen here ############

    # import pdb; pdb.set_trace()
    state_m = StateMachine(user)
    state_m.add_state('weekly_wet', INVESTMENT_TYPE, end_state='direct_wet')
    state_m.add_state('direct_wet', INVESTMENT_TYPE, end_state='binary')
    state_m.add_state('binary', INVESTMENT_TYPE, end_state='end')
    state_m.add_state('binary_wet', INVESTMENT_TYPE, end_state='end')


    state_m.set_start('weekly_wet')
    state_m.run(last_date, next_payout)
    state_m.set_start('direct_wet')
    state_m.run(last_date, next_payout)
    state_m.set_start('binary')
    state_m.run(last_date, next_payout, dry=True, date=None)
    state_m.set_start('binary_wet')
    state_m.run(last_date, next_payout)


    # print state_m.results
    binary, left_binary_cf, right_binary_cf = state_m.results['binary']
    direct = state_m.results['direct_wet']
    weekly = state_m.results['weekly_wet']

    # set current pkg calculations and carry forwards
    pkg.left_binary_cf = left_binary_cf
    pkg.right_binary_cf = right_binary_cf
    pkg.binary = binary
    pkg.direct = direct
    pkg.weekly = weekly

    print "weekly: {} direct: {} binary: {}".format(weekly, direct, binary)

    # Add Transactions
    # assert Transactions.objects.all()
    # Transactions.objects.create(sender_wallet=avicrypto_wallet, reciever_wallet=user_ROI_wallet, amount, tx_type="roi", status="P/C/processing/paid")
    bn_status = 'C' if pkg.binary_enable else 'P'
    today = UTC.normalize(UTC.localize(datetime.utcnow()))

    
    # sum the total transactions for this user since epoch
    kw = dict(
        avicrypto_wallet=avicrypto_wallet,
        user_ROI_wallet=user_ROI_wallet,
        user_DR_wallet=user_DR_wallet,
        user_BN_wallet=user_BN_wallet,
        user_btc=user_btc,
        user_xrp=user_xrp,
        user_eth=user_eth,
        avicrypto_btc=avicrypto_btc,
        avicrypto_xrp=avicrypto_xrp,
        avicrypto_eth=avicrypto_eth
    )

    start_dt = admin_param.get('start_dt', pkg.last_payout_date or EPOCH_BEGIN)
    end_dt = admin_param.get('end_dt', find_next_monday())
    if start_dt < end_dt:
        pkg.total_payout = calc_txns(start_dt, end_dt, **kw)
        pkg.last_payout_date = today
    pkg.save()


def calculate_investment(user, **kw):
    """Calculates all investment schemes of the user"""
    packages = User_packages.objects.filter(user=user, status='A')
    if packages:
        pkg = User_packages.objects.get(user=user, status='A')
        # last_date = pkg.last_payout_date
        last_date = START_TIME
        today = UTC.normalize(UTC.localize(datetime.utcnow()))
        next_payout = kw.get('next_date', find_next_monday())

        if last_date <= today < next_payout:
            # print "INSIDE calculate_investments"
            #print "calculating for ", user
            run_investment_calc(user, pkg, last_date, next_payout)


def run_scheduler(**kw):
    users = User.objects.all()
    divide_conquer(users, 0, len(users)-1,
                   lambda user: calculate_investment(user, **kw))




# def find_min_leg(user, last_date, next_date):
#     """Finds minimum of the two legs of `user` by aggregating their total package prices"""
#     left, right = get_left_right_agg(user)
#     return 'l' if left < right else 'r'


######## HARDCODED FOR NOW ################

def run_realtime_invest(user):    
    wallets = Wallet.objects.filter(owner=user)

    today = UTC.normalize(UTC.localize(datetime.utcnow()))

    Transactions.objects.filter(Q(reciever_wallet__in=[w for w in wallets])).exclude(tx_type='W').delete()
    admin_param = {
            'admin': User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us'),
            'start_dt': EPOCH_BEGIN,
            'end_dt': today  # UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 18)))
        }
    run_investment_calc(user, get_package(user), EPOCH_BEGIN, admin_param['end_dt'], **admin_param)