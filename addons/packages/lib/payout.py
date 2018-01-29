from addons.packages.models import Packages, User_packages
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer, get_left, get_right
from django.conf import settings
import pytz
import calendar
from datetime import datetime

UTC = pytz.UTC

START_TIME = getattr(settings, 'EPOCH_BEGIN', UTC.normalize(
    UTC.localize(datetime(2017, 12, 1, 00, 00, 00))))

# ################# direct sum calculation #######################
# TODO: Lotsa caching decorators


def calc_direct(user, last_date, next_date):
    """calculate the direct on each leg"""
    packages = User_packages.objects.filter(user=u)
    pkg = filter(lambda p: p.status == 'A', packages)
    assert len(pkg) == 1
    pkg = pkg[0]
    direct_payout = pkg.package.directout
    leg = find_min_leg(user)
    return calc_direct_leg(user, last_date, next_date, leg=leg) * direct_payout


def calc_direct_leg(user, last_date, next_date, leg='l'):
    check_leg = LEG[leg]
    sponsor_id = user.profile.user_auto_id
    # get `leg` members
    members = Members.objects.filter(parent_id=user.id)
    # filter members by `leg`
    filter_members = filter(check_leg, members)
    return calc_direct_sum(sponsor_id, last_date, next_date, filter_members)


def calc_direct_sum(sponsor_id, last_date, next_date, members):
    direct_users_sum = 0.0
    while members:
        # find active members' total direct sum in current cycle by sponsor id
        direct_users_sum += sum(map(lambda m: getattr(getattr(filter_by_active_package(
            m), 'package'), 'price'), filter_by_sponsor(sponsor_id, last_date, next_date, members)))
        # tree level traversal - get more members per child level
        members = reduce(lambda x, y: x+y, divide_conquer(members,
                                                          0, len(members), get_user_from_member))
    return direct_users_sum


# ################# Binary sum calculation #######################
def calc_binary():
    pass


# ################# Weekly sum calculation #######################
def calc_weekly():
    pass


# ############## Calculate Investment ###################
INVESTMENT_TYPE = {
    'direct': calc_direct,
    'binary': calc_binary,
    'weekly': calc_weekly
}


def calc(user, last_date, investment_type):
    """
    investment_type: can be direct, binary, weekly payouts
    Then set last_date = next_date
    """
    next_date = find_next_monday()
    return INVESTMENT_TYPE[investment_type](user, last_date, next_date)


def find_min_leg(user):
    """Finds minimum of the two legs of `user` by aggregating their total package prices"""
    return 'l' if calc_aggregate_left(user) < calc_aggregate_right(user) else 'r' 

def calc_aggregate_left(user):
    """Find the aggregate sum of all packages in left leg"""
    if user:
        left_user = get_left(user)
        packages = filter_by_active_package(user)
        if packages:    
            assert len(packages) == 1
            pkg = packages[0]
            return pkg.package.price + calc_aggregate_left(left_user) + calc_aggregate_right(left_user)
        return 0.0
    else:
        return 0.0

def calc_aggregate_right(user):
    """Find the aggregate sum of all packages in right leg"""
    if user:
        right_user = get_right(user)
        packages = filter_by_active_package(user)
        if packages:    
            assert len(packages) == 1
            pkg = packages[0]
            return pkg.package.price + calc_aggregate_left(right_user) + calc_aggregate_right(right_user)
        return 0.0
    else:
        return 0.0





# ############### HELPER FUNCTIONS ###############
def get_user_from_member(member):
    return Members.objects.filter(parent_id=member.child_id)

# filter functions


def filter_by_sponsor(sponsor_id, last_date, next_date, members):
    return [m for m in members if valid_payout_user(m, last_date, next_date)]
    # return filter(lambda member: member.child_id.profile.sponsor_id == sponsor_id, members)


def valid_payout_user(member, last_date, next_date):
    """Filter users that have their Date of Joining between last payout and next payout day"""
    doj = UTC.normalize(member.child_id.date_joined)
    # utc = pytz.UTC
    if doj.day == next_date.day:
        next_date = UTC.normalize(UTC.localize(datetime(
            next_date.year, next_date.month, next_date.day, doj.hour, doj.minute, doj.second, doj.microsecond)))
    return last_date <= doj < next_date


def filter_by_active_package(member):
    if type(member) == Members:
        child_id = member.child_id
    elif type(member) == User:
        child_id = member.id
    return filter(lambda p: p.status == 'A',
           User_packages.objects.filter(user=child_id))


def find_next_monday():
    """Finds next monday payout date"""
    cur_dt = UTC.normalize(UTC.localize(datetime.utcnow()))
    day = calendar.weekday(cur_dt.year, cur_dt.month, cur_dt.day)
    remaining_days = 7 - day
    return UTC.normalize(UTC.localize(datetime(cur_dt.year, cur_dt.month, cur_dt.day+remaining_days, cur_dt.hour, cur_dt.minute, cur_dt.second, cur_dt.microsecond)))
