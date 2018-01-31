from addons.accounts.models import User, Members
from addons.packages.models import Packages, User_packages
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer, get_left, get_right
from django.conf import settings
import pytz
import calendar
from datetime import datetime, timedelta

UTC = pytz.UTC

START_TIME = getattr(settings, 'EPOCH_BEGIN', UTC.normalize(
    UTC.localize(datetime(2017, 12, 1, 00, 00, 00))))

# ################# direct sum calculation #######################
# TODO: Lotsa caching decorators

def get_package(user):
    packages = User_packages.objects.filter(user=user)
    if packages:    
        pkg = filter(lambda p: p.status == 'A', packages)
        pkg = pkg[0]
        assert len(pkg) == 1
        return pkg
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


def calc_direct(user, last_date, next_date):
    """calculate the direct on each leg"""
    pkg = get_package(user)
    if pkg:    
        direct_payout = pkg.package.directout
        # finds leg with minimium total package prices
        leg = find_min_leg(user)
        return calc_leg(user, last_date, next_date, leg=leg) * direct_payout
    return 0.0
# ################# Binary sum calculation #######################


def calc_binary(user, last_date, next_date):
    """calculate the direct on each leg"""
    pairs = get_direct_pair(user, last_date, next_date)
    if pairs:
        pkg = get_package(user)
        if pkg:
            binary_payout = pkg.package.binary_payout
            # finds leg with minimium total package prices
            leg = find_min_leg(user)
            return calc_leg(user, last_date, next_date, leg=leg) * binary_payout
    return 0.0

# ################# Weekly sum calculation #######################


def calc_weekly():
    pass


def calc_leg(user, last_date, next_date, leg='l'):
    check_leg = LEG[leg]
    sponsor_id = user.profile.user_auto_id
    # get `leg` members
    members = Members.objects.filter(parent_id=user.id)
    # filter members by `leg`
    filter_members = filter(check_leg, members)
    return calc_sum(sponsor_id, last_date, next_date, filter_members)


def calc_sum(sponsor_id, last_date, next_date, members):
    users_sum = 0.0
    while members:
        # find active members' total package price sum in current cycle by sponsor id
        users_sum += sum(map(lambda m: getattr(getattr(filter_by_active_package(
            m), 'package'), 'price'), filter_by_sponsor(sponsor_id, last_date, next_date, members)))
        # tree level traversal - get more members per child level
        members = reduce(lambda x, y: x+y, divide_conquer(members,
                                                          0, len(members), get_user_from_member))
    return users_sum


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


def get_left_right_agg(user):
    """Returns True if left leg has lower aggregate package else False"""
    return (calc_aggregate_left(user), calc_aggregate_right(user))


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


def find_min_leg(user):
    """Finds minimum of the two legs of `user` by aggregating their total package prices"""
    left, right = get_left_right_agg(user)
    return 'l' if left < right else 'r'


# ############### HELPER FUNCTIONS ###############
def get_user_from_member(member):
    return Members.objects.filter(parent_id=member.child_id)

# filter functions


def filter_by_sponsor(sponsor_id, last_date, next_date, members):
    return [m for m in members if valid_payout_user(m, last_date, next_date)]


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
    remaining_days = (7 - day) % 7
    dt = datetime(cur_dt.year, cur_dt.month, cur_dt.day, cur_dt.hour,
                  cur_dt.minute, cur_dt.second, cur_dt.microsecond)
    rem_dt = timedelta(days=remaining_days)
    return UTC.normalize(UTC.localize(dt + rem_dt))
