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
    def wrapped_f(user, last_date, next_date):
        """
        Checks if user has active package else returns end state for relevant investment
        """
        pkg = get_package(user)
        if pkg:
            # print "calling %s with attr: %s, %s, %s" %(func.__name__, user.username, last_date, next_date)
            return func(user, last_date, next_date)
        else:
            return ((0.0, 0.0, 0.0), 'end') if func.__name__ == 'calc_binary' else (0.0, 'end')
    return wrapped_f


@is_eligible
def calc_direct(user, last_date, next_date):
    """calculate the direct:
        - For the cycle with time T for all T i.e. last_date <= T < next_date
        - filter users with (doj = T) and with active package
        - calculate their package price
        - sum * direct_payout %  
    """
    pkg = get_package(user)
    direct_payout = pkg.package.directout
    l_sum = calc_leg(user, last_date, next_date, leg='l')
    r_sum = calc_leg(user, last_date, next_date, leg='r')
    return ((l_sum + r_sum) * direct_payout/100.0, 'binary')


# ################# Binary sum calculation #######################
def calc_cf(left_sum, right_sum):
    """Calculates carry forward. 
    returns carry forward in the relevant leg"""
    res = abs(left_sum - right_sum)
    return (res, 0) if left_sum > right_sum else (0, res)


@is_eligible
def calc_binary(user, last_date, next_date):
    """calculate the binary on minimum of two legs"""
    # calculate if binary has atleast one direct pair
    pairs = get_direct_pair(user, last_date, next_date)
    if pairs:
        pkg = get_package(user)
        binary_payout = pkg.package.binary_payout/100.0
        # finds leg with minimium total package prices
        # leg = find_min_leg(user)
        # print "attrs: user {}\n last_date {}\n next_date {}\n".format(user.username, last_date, next_date)
        res = get_left_right_agg(user, last_date, next_date)
        # print "returned res is {}".format(res)
        left_sum, right_sum = res
        left_sum += pkg.left_binary_cf
        right_sum += pkg.right_binary_cf
        l_cf, r_cf = calc_cf(left_sum, right_sum)
        # TODO: add 'loyalty' when implemented
        return ((min(left_sum, right_sum) * binary_payout, l_cf, r_cf), 'end')
    return ((0.0, 0.0, 0.0), 'end')


################# DAILY CALCULATION #######################
@is_eligible
def calc_daily(user, last_date, next_date):
    from math import ceil, floor
    pkg = get_package(user)
    active_date = pkg.created_at.date()
    last_dt = greater_date(active_date, date(last_date.year, last_date.month, last_date.day))
    new_date = next_date.date()
    if last_dt < new_date:
        delta = new_date - last_dt
        days = floor(delta.days)
        return ((pkg.package.payout/100.) * pkg.package.price * days, 'direct')
    return (0.0, 'direct')

# ################# Weekly sum calculation #######################
@is_eligible
def calc_weekly(user, last_date, next_date):
    from math import ceil, floor
    # calculate number of weeks passed since last_date before next_date
    # print "for user %s" %(user.username)
    pkg = get_package(user)
    user_doj = pkg.created_at.date()
    # user_doj = user.date_joined.date()
    # user_doj = date(user_doj.year, user_doj.month, user_doj.day)
    old_date = greater_date(user_doj, date(last_date.year, last_date.month, last_date.day))
    new_date = next_date.date()
    if old_date < new_date:        
        # new_date = date(user_doj.year, user_doj.month, user_doj.day)
        delta = new_date - old_date
        num_weeks = floor(delta.days/7.0)
        # print "old date is {}, next_date is {}".format(old_date, next_date.date())
        # print "delta is %s" %delta
        # print "num of week: {}, old date is {}. new date is {}. difference in num weeks: {}".format(num_weeks, old_date, new_date, num_weeks)
        pkg = get_package(user)
        return ((pkg.package.payout/100.) * pkg.package.price * num_weeks, 'direct')
    return (0.0, 'direct')


def calc_leg(user, last_date, next_date, leg='l'):
    """Calculates sum of the total packages of members under a user sponsored by the user
    Uses function calc_sum"""
    check_leg = LEG[leg]
    sponsor_id = user.profile.user_auto_id
    # get `leg` members
    members = Members.objects.filter(parent_id=user.id)
    # filter members by `leg`
    filter_members = filter(check_leg, members)
    return calc_sum(sponsor_id, last_date, next_date, filter_members)


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


def calc_sum(sponsor_id, last_date, next_date, members):
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
                             filter_by_sponsor(sponsor_id, last_date, next_date, members)))
        # tree level traversal - get more members per child level
        # print "FUNCTION calc_sum > users_sum is: %s" %users_sum
        members = reduce(lambda x, y: x | y, divide_conquer(
            members, 0, len(members)-1, get_user_from_member))
        # [tot.append(m) for m in members]
    # print "users are: {}".format([m.child_id.username if type(m)==Members else m.username for m in tot])
    return users_sum


# ############## Calculate Investment ###################
INVESTMENT_TYPE = {
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


def calc_txns(start_dt, end_dt, **kw):
    """
    Calculates total payout between date ranges
    """
    return Transactions.objects.filter(sender_wallet=kw['avicrypto_wallet'], reciever_wallet = kw['user_ROI_wallet'], tx_type="roi", status='C', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    + Transactions.objects.filter(sender_wallet=kw['avicrypto_wallet'], reciever_wallet = kw['user_DR_wallet'], tx_type="direct", status='C', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    + Transactions.objects.filter(sender_wallet=kw['avicrypto_wallet'], reciever_wallet = kw['user_BN_wallet'], tx_type="binary", status='C', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    # deduct withdrawals from all wallet types
    - Transactions.objects.filter(sender_wallet=kw['user_btc'], reciever_wallet=kw['avicrypto_btc'], tx_type="W", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    - Transactions.objects.filter(sender_wallet=kw['user_xrp'], reciever_wallet =kw['avicrypto_xrp'], tx_type="W", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    - Transactions.objects.filter(sender_wallet=kw['user_eth'], reciever_wallet =kw['avicrypto_eth'], tx_type="W", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    # deduct user to user transfer from all wallet types
    - Transactions.objects.filter(sender_wallet=kw['user_btc'], tx_type="U", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    - Transactions.objects.filter(sender_wallet=kw['user_xrp'], tx_type="U", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    - Transactions.objects.filter(sender_wallet=kw['user_eth'], tx_type="U", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    # deduct topup from all wallet types
    - Transactions.objects.filter(sender_wallet=kw['user_btc'], tx_type="topup", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    - Transactions.objects.filter(sender_wallet=kw['user_xrp'], tx_type="topup", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))
    - Transactions.objects.filter(sender_wallet=kw['user_eth'], tx_type="topup", status='paid', datetime__range=(start_dt, end_dt)).values('datetime').annotate(data_sum=Sum('data'))


def run_investment_calc(user, pkg, last_date, next_payout):
    state_m = StateMachine(user)
    state_m.add_state('weekly', INVESTMENT_TYPE, end_state='direct')
    state_m.add_state('direct', INVESTMENT_TYPE, end_state='binary')
    state_m.add_state('binary', INVESTMENT_TYPE, end_state='end')
    # state_m.add_state('loyalty', INVESTMENT_TYPE, end_state='loyalty_booter')
    # state_m.add_state('loyalty_booter', INVESTMENT_TYPE, end_state='loyalty_booter_super')
    # state_m.add_state('loyalty_booter_super', INVESTMENT_TYPE, end_state='end')
    # print "end states:", state_m.end_states
    state_m.set_start('weekly')
    state_m.run(last_date, next_payout)
    state_m.set_start('direct')
    state_m.run(last_date, next_payout)
    state_m.set_start('binary')
    state_m.run(last_date, next_payout)

    # print state_m.results
    binary, left_binary_cf, right_binary_cf = state_m.results['binary']
    direct = state_m.results['direct']
    weekly = state_m.results['weekly']

    
    # get user and avicrypto wallets
    user_btc = Wallet.objects.filter(owner = user, wallet_type = 'BTC')
    user_eth = Wallet.objects.filter(owner = user, wallet_type = 'ETH')
    user_xrp = Wallet.objects.filter(owner = user, wallet_type = 'XRP')

    user_ROI_wallet = Wallet.objects.filter(owner = user, wallet_type = 'ROI')
    user_ROI_wallet = user_ROI_wallet[0] if user_ROI_wallet else Wallet.objects.create(owner = user, wallet_type = 'ROI')

    user_DR_wallet = Wallet.objects.filter(owner = user, wallet_type = 'DR')
    user_DR_wallet = user_DR_wallet[0] if user_DR_wallet else Wallet.objects.create(owner = user, wallet_type = 'DR')

    user_BN_wallet = Wallet.objects.filter(owner = user, wallet_type = 'BN')
    user_BN_wallet = user_BN_wallet[0] if user_BN_wallet else Wallet.objects.create(owner = user, wallet_type = 'BN')

    avicrypto_user = User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us')
    avicrypto_wallet = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'AW')
    avicrypto_wallet =  avicrypto_wallet[0] if avicrypto_wallet else Wallet.objects.create(owner = avicrypto_user, wallet_type = 'AW')
    
    avicrypto_btc = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'BTC')
    avicrypto_eth = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'ETH')
    avicrypto_xrp = Wallet.objects.filter(owner = avicrypto_user, wallet_type = 'XRP')

    # set current pkg calculations and carry forwards
    pkg.binary = binary
    pkg.left_binary_cf = left_binary_cf
    pkg.right_binary_cf = right_binary_cf
    pkg.direct = direct
    pkg.weekly = weekly

    # Add Transactions
    # Transactions.objects.create(sender_wallet=avicrypto_wallet, reciever_wallet=user_ROI_wallet, amount, tx_type="roi", status="P/C/processing/paid")
    bn_status = 'C' if pkg.binary_enable else 'P'
    today = UTC.normalize(UTC.localize(datetime.utcnow()))
    
    Transactions.objects.create(sender_wallet=avicrypto_wallet, reciever_wallet=user_ROI_wallet, amount = weekly, tx_type="roi", status="C")
    Transactions.objects.create(sender_wallet=avicrypto_wallet, reciever_wallet=user_DR_wallet, amount = direct, tx_type="direct", status="C")
    Transactions.objects.create(sender_wallet=avicrypto_wallet, reciever_wallet=user_BN_wallet, amount = binary, tx_type="binary", status=bn_status)
        
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
    
    pkg.total_payout = calc_txns(EPOCH_BEGIN , today, **kw)
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
def filter_by_sponsor(sponsor_id, last_date, next_date, members):
    # print "filter_by_sponsor members ", members
    return [m for m in members if valid_payout_user(sponsor_id, m, last_date, next_date)]


def valid_payout_user(sponsor_id, member, last_date, next_date):
    """Filter users that have their Date of Joining between last payout and next payout day"""
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
