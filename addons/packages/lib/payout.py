from addons.accounts.models import User, Members
from addons.packages.models import Packages, User_packages
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer, get_left, get_right
from django.conf import settings
import pytz
import calendar
from datetime import datetime, timedelta, date
from functools import wraps
from avicrypto.lib.dsm import StateMachine

UTC = pytz.UTC

START_TIME = getattr(settings, 'EPOCH_BEGIN', UTC.normalize(
    UTC.localize(datetime(2017, 12, 1, 00, 00, 00))))

# TODO: Lotsa caching decorators

# ################# direct sum calculation #######################
def get_package(user):
    packages = User_packages.objects.filter(user=user, status='A')
    if packages:
        packages = User_packages.objects.get(user=user, status='A')
        return packages if packages else None
    return None


def filter_by_leg_user(member, leg):
    """return only members of `leg`"""
    u = get_user_from_member(member)
    return LEG[leg](u)


def traverse_members(filtered_members, sponsor_id, last_date, next_date):
    # tree level traversal - get more members per child level
    child_members = map(get_user_from_member, filtered_members)
    # filter paying sponsored members
    child_members = filter_by_sponsor(
        sponsor_id, last_date, next_date, child_members)
    if child_members:
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
    left_members = filter(
        lambda m: filter_by_leg_user(m, 'l'), filtered_members)
    # filter only right `leg` members
    right_members = filter(
        lambda m: filter_by_leg_user(m, 'r'), filtered_members)
    # traverse left members
    left_members = traverse_members(
        left_members, sponsor_id, last_date, next_date)
    # traverse right members
    right_members = traverse_members(
        right_members, sponsor_id, last_date, next_date)
    # get total left and right count and return pairs
    l_count = len(left_members)
    r_count = len(right_members)
    diff = r_count - l_count if r_count > l_count else l_count - r_count
    return diff

def is_eligible(func):
    """Decorator for calculation function"""
    @wraps(func)
    def wrapped_f(user, last_date, next_date):
        """
        Checks if user has active package else returns end state for relevant investment
        """
        name = func.__name__
        pkg = get_package(user)
        if pkg:
            return func(user, last_date, next_date)
        else:
            return ((0.0, 0.0, 0.0), 'end') if name=='calc_binary' else (0.0, 'end') 
    return wrapped_f

@is_eligible
def calc_direct(user, last_date, next_date):
    """calculate the direct on each leg"""
    pkg = get_package(user)
    direct_payout = pkg.package.directout
    # finds leg with minimium total package prices
    leg = find_min_leg(user)
    return (calc_leg(user, last_date, next_date, leg=leg) * direct_payout, 'binary')


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
        binary_payout = pkg.package.binary_payout
        # finds leg with minimium total package prices
        # leg = find_min_leg(user)
        left_sum, right_sum = get_left_right_agg(user)
        left_sum += pkg.left_binary_cf
        right_sum += pkg.right_binary_cf
        l_cf, r_cf = calc_cf(left_sum, right_sum)
        return ((min(left_sum, right_sum) * binary_payout, l_cf, r_cf), 'end')  # TODO: add 'loyalty' when implemented
    return ((0.0, 0.0, 0.0), 'end')


# ################# Weekly sum calculation #######################
@is_eligible
def calc_weekly(user, last_date, next_date):
    # calculate number of weeks passed since last_date before next_date
    old_date = date(last_date.year, last_date.month, last_date.day)
    new_date = date.today()
    delta = new_date - old_date
    num_weeks = delta.days/7
    pkg = get_package(user)
    return ((pkg.package.payout/100.) * pkg.package.price * num_weeks, 'direct')


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


def get_active_mem_price(member):
    res = filter_by_active_package(member)
    return getattr(getattr(res, 'package'), 'price', 0) if res else 0.0


def calc_sum(sponsor_id, last_date, next_date, members):
    """Used for Direct Sum Calculation:
    Calculates total package price of all members under a user sponsored by that user"""
    users_sum = 0.0
    while members:
        # find active members' total package price sum in current cycle by sponsor id
        users_sum += sum(map(lambda m: get_active_mem_price(m),
                             filter_by_sponsor(sponsor_id, last_date, next_date, members)))
        # tree level traversal - get more members per child level
        members = reduce(lambda x, y: x+y, divide_conquer(members, 0, len(members)-1, get_user_from_member))
    return users_sum


# ############## Calculate Investment ###################
INVESTMENT_TYPE = {
    'direct': calc_direct,
    'binary': calc_binary,
    'weekly': calc_weekly,
}


def calc(user, last_date, investment_type):
    """
    investment_type: can be direct, binary, weekly payouts
    Then set last_date = next_date
    """
    next_date = find_next_monday()
    return INVESTMENT_TYPE[investment_type](user, last_date, next_date)


def calculate_investment(user):
    """Calculates all investment schemes of the user"""
    packages = User_packages.objects.filter(user=user, status='A')
    if packages:
        pkg = User_packages.objects.get(user=user, status='A')
        last_date = pkg.last_payout_date
        today = UTC.normalize(UTC.localize(datetime.utcnow()))
        next_payout = find_next_monday()
        if last_date <= today < next_payout:
            # print "INSIDE calculate_investments"
            state_m = StateMachine(user)
            
            state_m.add_state('weekly', INVESTMENT_TYPE, end_state='direct')
            state_m.add_state('direct', INVESTMENT_TYPE, end_state='binary')
            state_m.add_state('binary', INVESTMENT_TYPE, end_state='end')
            # state_m.add_state('loyalty', INVESTMENT_TYPE, end_state='end')
            # state_m.add_state('loyalty_booter', INVESTMENT_TYPE, end_state='end')
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
            
            pkg.binary = binary
            pkg.left_binary_cf = left_binary_cf
            pkg.right_binary_cf = right_binary_cf
            pkg.direct = direct
            pkg.weekly = weekly
            pkg.total_payout += binary + direct + weekly
            pkg.last_payout_date = next_payout
            pkg.save()


def run_scheduler():
    users = User.objects.all
    divide_conquer(users, 0, len(users)-1, calculate_investment)


def get_left_right_agg(user):
    """Returns aggregate package of both legs"""
    left_user = get_left(user)
    right_user = get_right(user)
    return (calc_aggregate_left(left_user), calc_aggregate_right(right_user))


def calc_aggregate_left(user):
    """Find the aggregate sum of all packages in left leg"""
    if user:
        left_user = get_left(user)
        pkg = get_package(user)
        if pkg:
            return pkg.package.price + calc_aggregate_left(left_user) + calc_aggregate_right(left_user)
        return 0.0
    else:
        return 0.0


def calc_aggregate_right(user):
    """Find the aggregate sum of all packages in right leg"""
    if user:
        right_user = get_right(user)
        pkg = get_package(user)
        if pkg:
            return pkg.package.price + calc_aggregate_left(right_user) + calc_aggregate_right(right_user)
        return 0.0
    else:
        return 0.0


def find_min_leg(user):
    """Finds minimum of the two legs of `user` by aggregating their total package prices"""
    left, right = get_left_right_agg(user)
    return 'l' if left < right else 'r'


# ############### HELPER FUNCTIONS ###############
def get_user_from_member(member):
    return Members.objects.filter(parent_id=member.child_id)

# filter functions


def filter_by_sponsor(sponsor_id, last_date, next_date, members):
    return [m for m in members if valid_payout_user(sponsor_id, m, last_date, next_date)]


def valid_payout_user(sponsor_id, member, last_date, next_date):
    """Filter users that have their Date of Joining between last payout and next payout day"""
    doj = UTC.normalize(member.child_id.date_joined)
    # utc = pytz.UTC
    if doj.day == next_date.day:
        next_date = UTC.normalize(UTC.localize(datetime(
            next_date.year, next_date.month, next_date.day, doj.hour, doj.minute, doj.second, doj.microsecond)))
    pkg = get_package(member.child_id)
    return (last_date <= doj < next_date) and (member.child_id.profile.sponsor_id == sponsor_id) and pkg


def filter_by_active_package(member):
    # print member, type(member)
    if type(member) == Members:
        child_id = member.child_id
    elif type(member) == User:
        child_id = member.id
    return get_package(child_id)


def find_next_monday():
    """Finds next monday payout date"""
    cur_dt = UTC.normalize(UTC.localize(datetime.utcnow()))
    day = calendar.weekday(cur_dt.year, cur_dt.month, cur_dt.day)
    remaining_days = (7 - day) % 7
    dt = datetime(cur_dt.year, cur_dt.month, cur_dt.day, cur_dt.hour,
                  cur_dt.minute, cur_dt.second, cur_dt.microsecond)
    rem_dt = timedelta(days=remaining_days)
    return UTC.normalize(UTC.localize(dt + rem_dt))
