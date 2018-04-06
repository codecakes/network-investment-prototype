from math import ceil, floor
from datetime import date
from django.db.models import Q
from payout_aux import get_package
from helpers import is_eligible, is_valid_date, greater_date, filter_by_sponsor, is_sponsored_by
from gen_txn import gen_txn_binary
from direct import get_direct_pair

from addons.accounts.models import Profile, Members, User
from addons.packages.models import Packages, User_packages
from addons.wallet.models import Wallet
from addons.transactions.models import Transactions
from addons.accounts.lib.tree import divide_conquer, LEG, get_left, get_right

import pdb;

def rec_binary(user, last_date, next_date, sponsor_user, sponsor_id):
    if not user:
        return
    l_user = get_left(user)
    r_user = get_right(user)

    members = Members.objects.filter(parent_id=user.id)
    # filter paying sponsored members by left and right branch
    filtered_members = filter_by_sponsor(sponsor_id, last_date, next_date, members, dry=True)
    [calc_binary(sponsor_user, last_date, next_date, dry=False, date=getattr(get_package(m.child_id), 'created_at', None)) for m in filtered_members]
    rec_binary(l_user, last_date, next_date, sponsor_user, sponsor_id)
    rec_binary(r_user, last_date, next_date, sponsor_user, sponsor_id)
    return [], 'end'


def binary_wet(user, last_date, next_date):
    """
    - Do recursive Traverse left and right
    - Find if last_date <= Pkg activation date falls < next_date
    - If so, calc_binary
    - Once exhausted, exit
    """
    # calculate if binary has atleast one direct pair
    # It can happen that binary gets calculated and yet there is not direct pair. 
    # In that case binary gets set to txn type='P' viz Pending
    pairs = get_direct_pair(user, last_date, next_date)
    pkg = get_package(user)
    if pairs:
        pkg.binary_enable = True
        pkg.save()
        assert pkg.binary_enable
        assert pairs

        # switch all Pending Transactions to Confirmed status
        user_BN_wallet = Wallet.objects.filter(
            owner=user, wallet_type='BN').first()
        
        avicrypto_user = User.objects.get(
            username='harshul', email='harshul.kaushik@avicrypto.us')
        avicrypto_wallet = Wallet.objects.filter(
            owner=avicrypto_user, wallet_type='AW').first()
        
        bn_status = 'C' if pkg.binary_enable else 'P'
        # set txns's status to 'Confirmed' from Pending
        Transactions.objects.filter(
            sender_wallet=avicrypto_wallet,
            reciever_wallet=user_BN_wallet,
            tx_type="binary", status='P'
        ).update(status=bn_status)
   
    sponsor_id = user.profile.user_auto_id
    return rec_binary(user, last_date, next_date, user, sponsor_id)


@gen_txn_binary
@is_eligible
def calc_binary(user, last_date, next_date, dry=True, date=None):
    """calculate the binary on minimum of two legs"""

    pdb.pprint.pprint([pkg.weekly, pkg.direct, pkg.binary, pairs])
    # assert pkg.direct > 0.
    binary_payout = pkg.package.binary_payout/100.0
    # finds leg with minimium total package prices
    res = get_left_right_agg(user, last_date, next_date)
    left_sum, right_sum = res
    left_sum += pkg.left_binary_cf
    right_sum += pkg.right_binary_cf
    l_cf, r_cf = calc_cf(left_sum, right_sum)
    final_amt = round(min(left_sum, right_sum) * binary_payout, 2)
    return ((final_amt, l_cf, r_cf), 'end')


@is_eligible
def get_left_right_agg(user, last_date, next_date):
    """Returns aggregate package of both legs"""
    left_user = get_left(user)
    right_user = get_right(user)
    #print "left user {} and right users {}".format(left_user.username, right_user.username)
    return [calc_aggregate_left(left_user, user, last_date, next_date), calc_aggregate_right(right_user, user, last_date, next_date)]




@is_valid_date
def calc_aggregate_left(user, sponsor_user, last_date, next_date):
    """Find the aggregate sum of all packages in left leg"""
    if user:
        left_user = get_left(user)
        pkg = get_package(user)
        if pkg:
            price = pkg.package.price if is_sponsored_by(user, sponsor_user) else 0
            return price + calc_aggregate_left(left_user, sponsor_user, last_date, next_date) + calc_aggregate_right(left_user, sponsor_user, last_date, next_date)
        return 0.0
    return 0.0

# @gen_txn_binary


@is_valid_date
def calc_aggregate_right(user, sponsor_user, last_date, next_date):
    """Find the aggregate sum of all packages in right leg"""
    if user:
        right_user = get_right(user)
        pkg = get_package(user)
        if pkg:
            price = pkg.package.price if is_sponsored_by(user, sponsor_user) else 0
            return price + calc_aggregate_left(right_user, sponsor_user, last_date, next_date) + calc_aggregate_right(right_user, sponsor_user, last_date, next_date)
        return 0.0
    return 0.0


def calc_cf(left_sum, right_sum):
    """Calculates carry forward. 
    returns carry forward in the relevant leg"""
    res = abs(left_sum - right_sum)
    return (res, 0) if left_sum > right_sum else (0, res)
