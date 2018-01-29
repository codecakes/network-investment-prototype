from addons.packages.models import Packages, User_packages
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer
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
    pkg = [pkg]
    direct_payout = pkg.package.directout
    return min(calc_direct_leg(user, last_date, next_date, leg='l'), calc_direct_leg(user, last_date, next_date, leg='r')) * direct_payout


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
    filter(lambda p: p.status == 'A',
           User_packages.objects.filter(user=member.child_id))


def find_next_monday():
    """Finds next monday payout date"""
    cur_dt = UTC.normalize(UTC.localize(datetime.utcnow()))
    day = calendar.weekday(cur_dt.year, cur_dt.month, cur_dt.day)
    remaining_days = 7 - day
    return UTC.normalize(UTC.localize(datetime(cur_dt.year, cur_dt.month, cur_dt.day+remaining_days, cur_dt.hour, cur_dt.minute, cur_dt.second, cur_dt.microsecond)))
