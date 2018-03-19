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


UTC = pytz.UTC

EPOCH_BEGIN = START_TIME = getattr(settings, 'EPOCH_BEGIN', UTC.normalize(
    UTC.localize(datetime(2017, 12, 1, 00, 00, 00))))

# TODO: Lotsa caching decorators

# ################# direct sum calculation #######################


def get_package(user):
    packages = User_packages.objects.filter(user=user, status='A')
    if packages:
        # packages = User_packages.objects.get(user=user, status='A')
        return packages[0] if packages else None
    return None


def filter_by_leg_user(member, leg):
    """return only members of `leg`"""
    u = get_user_from_member(member)
    return LEG[leg](u)


def traverse_members(filtered_members, sponsor_id, last_date, next_date):
    # tree level traversal - get more members per child level
    # child_members = map(get_user_from_member, filtered_members)
    child_members = reduce(lambda x, y: x | y, [Members.objects.filter(
        parent_id=m.child_id) for m in filtered_members])
    # filter paying sponsored members
    child_members = filter_by_sponsor(
        sponsor_id, last_date, next_date, child_members)
    if len(child_members):
        #print "child_members is", child_members
        # res = traverse_members(child_members, sponsor_id, last_date, next_date)
        # print "traverse_members is ", res
        return filtered_members + traverse_members(child_members, sponsor_id, last_date, next_date)
    else:
        return []


def get_direct_pair(user, last_date, next_date):
    """calculate the direct pair on each leg
    - calculate for `l` and `r` leg, 
    total activated direct nodes between last payout date and next payout date
    - calculate and return how many pairs they make
    """
    sponsor_id = user.profile.user_auto_id
    members = Members.objects.filter(parent_id=user.id)
    # filter paying sponsored members
    filtered_members = filter_by_sponsor(
        sponsor_id, last_date, next_date, members)
    # filter only left `leg` members
    # left_members = filter(
    #     lambda m: filter_by_leg_user(m, 'l'), filtered_members)
    left_members = filter(
        lambda m: LEG['l'](m), filtered_members)
    # filter only right `leg` members
    # right_members = filter(
    #     lambda m: filter_by_leg_user(m, 'r'), filtered_members)
    right_members = filter(
        lambda m: LEG['r'](m), filtered_members)

    active_left = User_packages.objects.filter(
        user=left_members[0].child_id, status='A') if left_members else None
    active_right = User_packages.objects.filter(
        user=right_members[0].child_id, status='A') if right_members else None
    return True if (active_left and active_right) else False
    # # traverse left members
    # left_members = traverse_members(
    #     left_members, sponsor_id, last_date, next_date)
    # # traverse right members
    # right_members = traverse_members(
    #     right_members, sponsor_id, last_date, next_date)
    # # get total left and right count and return pairs
    # l_count = len(left_members)
    # r_count = len(right_members)
    # print [m.parent_id.profile.user_auto_id for m in left_members+right_members]
    # print l_count, r_count
    # diff = r_count - l_count if r_count > l_count else l_count - r_count
    # return diff


def is_valid_date(func):
    """Decorator for calculation function"""
    @wraps(func)
    def wrapped_f(user, last_date, next_date):
        """
        Checks if user falls within valid date range else bypasses to its children 0
        """
        if user:
            pkg = get_package(user)
            if pkg:
                doj = UTC.normalize(pkg.created_at)
                # doj = UTC.normalize(user.date_joined)
                if last_date <= doj < next_date:
                    #print "in if is valid_date  "
                    #print "func name is {}".format(func.__name__)
                    return func(user, last_date, next_date)
                elif func.__name__ == "get_left_right_agg":
                    return (0.0, 0.0)
                # elif doj == next_date:
                #     return 0.0
                # else:
                #     print "in else is valid_date "
                #     print "last_date <= doj < next_date is: {} <= {} < {}".format(last_date, doj, next_date)
                #     print "user valid date check", user.username
                #     return get_left_right_agg(user, last_date, next_date)
        return 0.0
    return wrapped_f


def is_eligible(func):
    """Decorator for calculation function"""
    @wraps(func)
    def wrapped_f(*args, **kw):
        """
        Checks if user has active package else returns end state for relevant investment
        """
        print "inside is_eligible. calling %s"%func.__name__
        user, last_date, next_date = args[:3]
        pkg = get_package(user)
        if pkg:
            # print "calling %s with attr: %s, %s, %s" %(func.__name__, user.username, last_date, next_date)
            return func(*args, **kw)
        else:
            return ((0.0, 0.0, 0.0), 'end') if 'binary' in func.__name__ else (0.0, 'end')
    return wrapped_f


def direct_wet(user, last_date, next_date):
    return calc_direct(user, last_date, next_date, dry=False)


@is_eligible
def calc_direct(user, last_date, next_date, dry=True):
    """calculate the direct:
        - For the cycle with time T for all T i.e. last_date <= T < next_date
        - filter users with (doj = T) and with active package
        - calculate their package price
        - sum * direct_payout %  
    """
    pkg = get_package(user)
    direct_payout = pkg.package.directout
    l_sum = calc_leg(user, last_date, next_date, leg='l', dry=dry)
    r_sum = calc_leg(user, last_date, next_date, leg='r', dry=dry)
    return ((l_sum + r_sum) * direct_payout/100.0, 'binary')


# ################# Binary sum calculation #######################
def calc_cf(left_sum, right_sum):
    """Calculates carry forward. 
    returns carry forward in the relevant leg"""
    res = abs(left_sum - right_sum)
    return (res, 0) if left_sum > right_sum else (0, res)


def gen_txn_binary(func):
    @wraps(func)
    def wrapped_f(user, last_date, next_date, dry, date):
        res = func(user, last_date, next_date, dry=dry, date=date)
        calc, _ = res
        binary_payout, l_cf, r_cf = calc
        if not dry and date:
            # print "generating binary transaction"
            pkg = get_package(user)
            user_BN_wallet = Wallet.objects.filter(
                owner=user, wallet_type='BN').first()
            
            avicrypto_user = User.objects.get(
                username='harshul', email='harshul.kaushik@avicrypto.us')
            avicrypto_wallet = Wallet.objects.filter(
                owner=avicrypto_user, wallet_type='AW').first()
            
            bn_status = 'C' if pkg.binary_enable else 'P'
            bn_txn = Transactions.objects.create(
                sender_wallet=avicrypto_wallet, 
                reciever_wallet=user_BN_wallet, 
                amount=binary_payout, 
                tx_type="binary", status=bn_status)
            bn_txn.created_at = date
            bn_txn.save(update_fields=['created_at'])
            
            assert Transactions.objects.all()
            # print "transaction generated"
        return res
    return wrapped_f


def binary_wet(user, last_date, next_date):
    return calc_binary(user, last_date, next_date, dry=False, date=None)


@gen_txn_binary
@is_eligible
def calc_binary(user, last_date, next_date, dry=True, date=None):
    """calculate the binary on minimum of two legs"""
    # calculate if binary has atleast one direct pair
    pairs = get_direct_pair(user, last_date, next_date)
    pkg = get_package(user)
    if pairs:
        pkg.binary_enable = True
        pkg.save()

    binary_payout = pkg.package.binary_payout/100.0
    # finds leg with minimium total package prices
    res = get_left_right_agg(user, last_date, next_date)
    left_sum, right_sum = res
    left_sum += pkg.left_binary_cf
    right_sum += pkg.right_binary_cf
    l_cf, r_cf = calc_cf(left_sum, right_sum)
    return ((min(left_sum, right_sum) * binary_payout, l_cf, r_cf), 'end')
    # return ((0.0, 0.0, 0.0), 'end')


################# DAILY CALCULATION #######################
@is_eligible
def calc_daily(user, last_date, next_date):
    from math import ceil, floor
    pkg = get_package(user)
    active_date = pkg.created_at.date()
    last_dt = greater_date(active_date, date(
        last_date.year, last_date.month, last_date.day))
    new_date = next_date.date()
    if last_dt < new_date:
        delta = new_date - last_dt
        days = floor(delta.days)
        return ((pkg.package.payout/100.) * pkg.package.price * days, 'direct')
    return (0.0, 'direct')

#### GENERATE TRANSACTION ####


def gen_txn_weekly(week_num, old_date, new_date, user, weekly_payout):
    """calculate for which TIMESTAMP is the Transaction to be generated"""

    print "inside gen_txn_weekly"
    rem_dt = timedelta(days=7*week_num)
    old_date_time = datetime(old_date.year, old_date.month, old_date.day)
    dt = UTC.normalize(UTC.localize(old_date_time + rem_dt))
    if dt.date() <= new_date:
        user_ROI_wallet = Wallet.objects.filter(owner=user, wallet_type='ROI').first()

        avicrypto_user = User.objects.get(username='harshul', email='harshul.kaushik@avicrypto.us')
        avicrypto_wallet = Wallet.objects.filter(
            owner=avicrypto_user, wallet_type='AW').first()
        
        roi_txn = Transactions.objects.create(
            sender_wallet=avicrypto_wallet, 
            reciever_wallet=user_ROI_wallet, 
            amount=weekly_payout, 
            tx_type="roi", status="C")
        roi_txn.created_at = find_next_monday()
        roi_txn.save(update_fields=['created_at'])
        assert Transactions.objects.all()
        # print "asserted Txns"
    return

# ################# Weekly sum calculation #######################


def weekly_wet(user, last_date, next_date):
    # print "inside weekly_wet"
    return calc_weekly(user, last_date, next_date, dry=False)


@is_eligible
def calc_weekly(user, last_date, next_date, dry=True):
    from math import ceil, floor
    # calculate number of weeks passed since last_date before next_date
    # print "for user %s" %(user.username)
    pkg = get_package(user)
    user_doj = pkg.created_at.date()
    num_weeks = 0
    # user_doj = user.date_joined.date()
    # user_doj = date(user_doj.year, user_doj.month, user_doj.day)
    old_date = greater_date(user_doj, date(
        last_date.year, last_date.month, last_date.day))
    new_date = next_date.date()
    if old_date < new_date:
        # new_date = date(user_doj.year, user_doj.month, user_doj.day)
        delta = new_date - old_date
        num_weeks = floor(delta.days/7.0)
        # print "old date is {}, next_date is {}".format(old_date, next_date.date())
        # print "delta is %s" %delta
        # print "num of week: {}, old date is {}. new date is {}. difference in num weeks: {}".format(num_weeks, old_date, new_date, num_weeks)
        pkg = get_package(user)
        payout = (pkg.package.payout/100.) * pkg.package.price
        res = (payout * num_weeks, 'direct')
    else:
        res = payout, _ = (0.0, 'direct')
    # print "dry is %s"%dry
    if dry == False:
        # print "running weekly divide_conquer with num weeks = %s"%num_weeks

        if num_weeks:
            divide_conquer(range(int(num_weeks)), 0, int(num_weeks) - 1,
                       lambda num: gen_txn_weekly(num, old_date, new_date, user, payout))
    return res


def calc_leg(user, last_date, next_date, leg='l', dry=True):
    """Calculates sum of the total packages of members under a user sponsored by the user
    Uses function calc_sum"""
    check_leg = LEG[leg]
    sponsor_id = user.profile.user_auto_id
    # get `leg` members
    members = Members.objects.filter(parent_id=user.id)
    # filter members by `leg`
    filter_members = filter(check_leg, members)
    return calc_sum(sponsor_id, last_date, next_date, filter_members, dry=dry)


def filter_by_active_package(member):
    # print member, type(member)
    if type(member) == Members:
        child_id = member.child_id
    elif type(member) == User:
        child_id = member.id
    return get_package(child_id)


def get_active_mem_price(member):
    res = filter_by_active_package(member)
    if res:
        return res.package.price
    return 0.0


def calc_sum(sponsor_id, last_date, next_date, members, dry=True):
    """Used for Direct Sum Calculation:
    Calculates total package price of all members under a user sponsored by that user"""
    users_sum = 0.0
    # u = User.objects.get(username=sponsor_id)
    profile = Profile.objects.get(user_auto_id=sponsor_id)
    u = profile.user
    # print "u is {}".format(u)
    # tot = [u]
    # print "members {}".format([m.child_id.username for m in members])
    # [tot.append(m) for m in members]
    while members:
        # find active members' total package price sum in current cycle by sponsor id
        users_sum += sum(map(lambda m: get_active_mem_price(m),
                             filter_by_sponsor(sponsor_id, last_date, next_date, members, dry=dry)))
        # tree level traversal - get more members per child level
        # print "FUNCTION calc_sum > users_sum is: %s" %users_sum
        members = reduce(lambda x, y: x | y, divide_conquer(
            members, 0, len(members)-1, get_user_from_member))
        # [tot.append(m) for m in members]
    # print "users are: {}".format([m.child_id.username if type(m)==Members else m.username for m in tot])
    return users_sum


# ############## Calculate Investment ###################
INVESTMENT_TYPE = {
    'weekly_wet': weekly_wet,
    'direct_wet': direct_wet,
    'binary_wet': binary_wet,
    'direct': calc_direct,
    'binary': calc_binary,
    'weekly': calc_weekly,
    'daily': calc_daily
}


def calc(user, last_date, investment_type):
    """
    investment_tytepe: can be direct, binary, weekly payouts
    Then set last_date = next_date
    """
    next_date = find_next_monday()
    return INVESTMENT_TYPE[investment_type](user, last_date, next_date)


def calc_txns_reducer(txn_obj):
    # print "txn_obj is {}".format(txn_obj)
    # pdb.set_trace()
    if type(txn_obj) == float:
        return txn_obj
    return txn_obj.data_sum
    # print txn_obj
    # if txn_obj:
    #     if txn_obj[0]:
    #         return txn_obj[0].data_sum
    # if txn_obj.values():
    #     if txn_obj.values()[0]['data_sum']:
    #         return txn_obj.values()[0]['data_sum']
    # return 0.0


def calc_txns(start_dt, end_dt, **kw):
    """
    Calculates total payout between date ranges
    """
    import pdb
    pdb.pprint.pprint(kw, depth=2)

    assert Transactions.objects.all()
    sum_subquery = Q(reciever_wallet__in=[
        kw['user_ROI_wallet'],
        kw['user_DR_wallet'],
        kw['user_BN_wallet'] 
        ]) & Q(tx_type__in=["roi", "direct", "binary"]) & Q(status__in=["C", "P", "processing", "paid"])
        # & Q(sender_wallet=kw['avicrypto_wallet']) & 
    sum_txns = Transactions.objects.filter(sum_subquery, created_at__range=(start_dt, end_dt)).annotate(data_sum=Sum('amount'))
    

    diff_subquery = Q(reciever_wallet=kw['user_btc']) | Q(reciever_wallet=kw['user_eth']) | Q(reciever_wallet=kw['user_xrp']) & Q(tx_type__in=["W", "U", "topup"]) & Q(status__in=["pending", "processing", "C", "paid"])
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
    return agg - diff if diff_txns else agg


def update_wallet_dt(user, wallet, wallet_type, last_date):
    wallet = wallet.first() if wallet else Wallet.objects.create(owner=user, wallet_type=wallet_type)
    p = Profile.objects.get(user=user)
    wallet.created_at = p.created_at if wallet.created_at > p.created_at else wallet.created_at
    wallet.save(update_fields=['created_at'])
    return wallet
    
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

    state_m.set_start('weekly_wet')
    state_m.run(last_date, next_payout)
    state_m.set_start('direct_wet')
    state_m.run(last_date, next_payout)
    state_m.set_start('binary')
    state_m.run(last_date, next_payout, dry=True, date=None)

    # print state_m.results
    binary, left_binary_cf, right_binary_cf = state_m.results['binary']
    direct = state_m.results['direct_wet']
    weekly = state_m.results['weekly_wet']

    # set current pkg calculations and carry forwards
    pkg.binary = binary
    pkg.left_binary_cf = left_binary_cf
    pkg.right_binary_cf = right_binary_cf
    pkg.direct = direct
    pkg.weekly = weekly

    print "weekly: {} direct: {} binary: {}".format(weekly, direct, binary)

    # Add Transactions
    assert Transactions.objects.all()
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


# @is_valid_date
@is_eligible
def get_left_right_agg(user, last_date, next_date):
    """Returns aggregate package of both legs"""
    left_user = get_left(user)
    right_user = get_right(user)
    #print "left user {} and right users {}".format(left_user.username, right_user.username)
    return [calc_aggregate_left(left_user, last_date, next_date), calc_aggregate_right(right_user, last_date, next_date)]

# @gen_txn_binary


@is_valid_date
def calc_aggregate_left(user, last_date, next_date):
    """Find the aggregate sum of all packages in left leg"""
    if user:
        left_user = get_left(user)
        pkg = get_package(user)
        if pkg:
            return pkg.package.price + calc_aggregate_left(left_user, last_date, next_date) + calc_aggregate_right(left_user, last_date, next_date)
        return 0.0
    return 0.0

# @gen_txn_binary


@is_valid_date
def calc_aggregate_right(user, last_date, next_date):
    """Find the aggregate sum of all packages in right leg"""
    if user:
        right_user = get_right(user)
        pkg = get_package(user)
        if pkg:
            return pkg.package.price + calc_aggregate_left(right_user, last_date, next_date) + calc_aggregate_right(right_user, last_date, next_date)
        return 0.0
    return 0.0


def find_min_leg(user, last_date, next_date):
    """Finds minimum of the two legs of `user` by aggregating their total package prices"""
    left, right = get_left_right_agg(user)
    return 'l' if left < right else 'r'


# ############### HELPER FUNCTIONS ###############
def get_user_from_member(member):
    res = Members.objects.filter(parent_id=member.child_id)
    # print "get_user_from_member", res
    return res


# filter functions
def filter_by_sponsor(sponsor_id, last_date, next_date, members, dry=True):
    # print "filter_by_sponsor members ", members
    return [m for m in members if valid_payout_user(sponsor_id, m, last_date, next_date, dry=dry)]


def gen_txn_direct(func):
    @wraps(func)
    def wrapped_f(sponsor_id, member, last_date, next_date, dry):
        res = func(sponsor_id, member, last_date, next_date, dry=dry)
        if res and dry == False:
            # print "generating direct transaction. sponsor_id is %s"%sponsor_id
            p = Profile.objects.get(user_auto_id=sponsor_id)
            sponsor_user = p.user
            doj = UTC.normalize(member.child_id.date_joined)
            pkg = get_package(sponsor_user)

            assert type(member.child_id) == User
            child_pkg = get_package(member.child_id)
            # print "child_pkg is ", child_pkg, member.child_id.username, 

            dr = (pkg.package.directout/100.0) * child_pkg.package.price

            user_DR_wallet = Wallet.objects.filter(
                owner=sponsor_user, wallet_type='DR').first()

            avicrypto_user = User.objects.get(
                username='harshul', email='harshul.kaushik@avicrypto.us')
            avicrypto_wallet = Wallet.objects.filter(
                owner=avicrypto_user, wallet_type='AW').first()
            
            dr_txn = Transactions.objects.create(
                sender_wallet=avicrypto_wallet, reciever_wallet=user_DR_wallet, amount=dr, tx_type="direct", status="C")
            dr_txn.created_at = child_pkg.package.created_at
            dr_txn.save(update_fields=['created_at'])
            
            assert Transactions.objects.all()
            # print "Txn asserted"

            calc_binary(sponsor_user, last_date, next_date, dry=False,
                        date=child_pkg.package.created_at)
        return res
    return wrapped_f


@gen_txn_direct
def valid_payout_user(sponsor_id, member, last_date, next_date, dry=True):
    """Filter users that have their Date of Joining between last payout and next payout day
    - params:
        dry: For dry run, no side-effect function if True. If False, generates a Direct Type Transaction. Defaults to True.
    """
    # print "member is", member
    # pkg = get_package(member.child_id)
    doj = UTC.normalize(member.child_id.date_joined)
    # utc = pytz.UTC
    # if doj.day == next_date.day:
    #     next_date = UTC.normalize(UTC.localize(datetime(
    #         next_date.year, next_date.month, next_date.day, doj.hour, doj.minute, doj.second, doj.microsecond)))

    # check if member is active
    pkg = get_package(member.child_id)
    # check if member falls within this cycle.
    # check if is a direct sponsor
    # print "member is ", member.child_id.username
    # print "member.child_id.profile.sponser_id ", member.child_id.profile.sponser_id
    try:
        return (last_date <= doj < next_date) and (member.child_id.profile.sponser_id.profile.user_auto_id == sponsor_id) and pkg
    except:
        return False


def find_next_monday():
    """Finds next monday payout date"""
    cur_dt = UTC.normalize(UTC.localize(datetime.utcnow()))
    day = calendar.weekday(cur_dt.year, cur_dt.month, cur_dt.day)
    remaining_days = (7 - day) % 7
    dt = datetime(cur_dt.year, cur_dt.month, cur_dt.day, cur_dt.hour,
                  cur_dt.minute, cur_dt.second, cur_dt.microsecond)
    rem_dt = timedelta(days=remaining_days)
    return UTC.normalize(UTC.localize(dt + rem_dt)) if remaining_days != 0 else UTC.normalize(UTC.localize(dt + timedelta(days=7)))


def greater_date(dt1, dt2):
    return max(dt1, dt2)
