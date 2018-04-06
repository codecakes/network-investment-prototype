from math import ceil, floor
from datetime import date
from payout_aux import get_package
from helpers import is_eligible, is_valid_date, greater_date, filter_by_sponsor, filter_by_sponsor_direct
from addons.accounts.lib.tree import divide_conquer, LEG, get_left, get_right
from gen_txn import gen_txn_direct

from addons.accounts.models import Profile, Members, User


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
    final_amt = round((l_sum + r_sum) * direct_payout/100.0, 2)
    return (final_amt, 'binary')


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


def calc_sum(sponsor_id, last_date, next_date, members, dry=True):
    """Used for Direct Sum Calculation:
    Calculates total package price of all members under a user sponsored by that user"""
    users_sum = 0.0
    profile = Profile.objects.get(user_auto_id=sponsor_id)
    u = profile.user
    while members:
        # find active members' total package price sum in current cycle by sponsor id
        users_sum += sum(map(lambda m: get_active_mem_price(m),
                             filter_by_sponsor(sponsor_id, last_date, next_date, members, dry=dry)))
        # tree level traversal - get more members per child level
        members = reduce(lambda x, y: x | y, divide_conquer(
            members, 0, len(members)-1, get_user_from_member))    
    return users_sum


def get_active_mem_price(member):
    res = filter_by_active_package(member)
    if res:
        return res.package.price
    return 0.0


def filter_by_active_package(member):
    # print member, type(member)
    if type(member) == Members:
        child_id = member.child_id
    elif type(member) == User:
        child_id = member.id
    return get_package(child_id)


def get_user_from_member(member):
    return Members.objects.filter(parent_id=member.child_id)


def find_pair(user, last_date, next_date, sponsor_id):
    """
    Find if left subtree and right subtree points to sponsor_id
    - traverse left
        - filter by sponsor
    - traverse right
        - filter by sponsor
    - if sponsor == user, return else continue traverse
    - if EOL, return False
    """
    if not user:
        return False

    l_user = get_left(user)
    r_user = get_right(user)

    members = Members.objects.filter(parent_id=user.id)
    # filter paying sponsored members by left and right branch
    filtered_members = filter_by_sponsor_direct(
        sponsor_id, last_date, next_date, members, dry=True)
    
    active_left_members = filter(
        lambda m: LEG['l'](m), filtered_members)
    active_right_members = filter(
        lambda m: LEG['r'](m), filtered_members)

    # return True if both True else keep traversing
    if active_left_members:
        l_bool = True
    else:
        l_bool = find_pair(l_user, last_date, next_date, sponsor_id)

    if active_right_members:
        r_bool = True
    else:
        r_bool = find_pair(r_user, last_date, next_date, sponsor_id)

    return l_bool and r_bool


def get_direct_pair(user, last_date, next_date):
    """calculate the direct pair on each leg"""
    sponsor_id = user.profile.user_auto_id
    return find_pair(user, last_date, next_date, sponsor_id)
