from math import floor
from functools import wraps
from datetime import timedelta, datetime
from pytz import UTC
from addons.wallet.models import Wallet
from addons.transactions.models import Transactions
from addons.accounts.models import User, Profile

from payout_aux import get_package

import pdb

#### GENERATE TRANSACTION ####


################# DAILY CALCULATION #######################
# @is_eligible
def calc_daily(user, last_date, next_date):
    pkg = get_package(user)
    active_date = pkg.created_at.date()
    # last_dt = greater_date(active_date, date(last_date.year, last_date.month, last_date.day))
    if last_date < next_date:
        delta = next_date - last_date
        days = floor(delta.days)
        final_amt = round((pkg.package.payout/100.0) * pkg.package.price * days/7.0, 2)
        return (final_amt, 'direct')
    return (0.0, 'direct')


def gen_txn_weekly(week_num, old_date, new_date, user, weekly_payout):
    """calculate for which TIMESTAMP is the Transaction to be generated"""
    rem_dt = timedelta(days=7*week_num)
    old_date_time = datetime(old_date.year, old_date.month, old_date.day)
    dt = UTC.normalize(UTC.localize(old_date_time + rem_dt))
    new_date_time = UTC.normalize(UTC.localize(datetime(new_date.year, new_date.month, new_date.day)))
    if dt <= new_date_time:
        user_ROI_wallet = Wallet.objects.filter(owner=user, wallet_type='ROI').first()
        avicrypto_user = User.objects.get(username='harshul', email='harshul.kaushik@avicrypto.us')
        avicrypto_wallet = Wallet.objects.filter(
            owner=avicrypto_user, wallet_type='AW').first()
        
        roi_txn = Transactions.objects.create(
            sender_wallet=avicrypto_wallet,
            reciever_wallet=user_ROI_wallet, 
            amount=calc_daily(user, dt, new_date_time)[0],
            tx_type="roi", status="C")
        roi_txn.created_at = min(dt, new_date_time)
        roi_txn.save(update_fields=['created_at'])
        # assert Transactions.objects.all()
    return


def gen_txn_direct(func):
    @wraps(func)
    def wrapped_f(sponsor_id, member, last_date, next_date, dry):
        # put on func = valid_payout_user
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
            
            # assert Transactions.objects.all()
            # print "Txn asserted"

            # calc_binary(sponsor_user, last_date, next_date, dry=False,
            #             date=child_pkg.package.created_at)
        return res
    return wrapped_f


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
            print "This Binary Txn type is.."
            pdb.pprint.pprint(bn_txn.status)
            
            # assert Transactions.objects.all()
            # print "transaction generated"
        return res
    return wrapped_f

