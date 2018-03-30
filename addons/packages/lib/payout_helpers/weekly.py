from math import ceil, floor
from datetime import date
from payout_aux import get_package
from helpers import is_eligible, is_valid_date, greater_date
from addons.accounts.lib.tree import divide_conquer
from gen_txn import gen_txn_weekly, calc_daily



# ################# Weekly sum calculation #######################


def weekly_wet(user, last_date, next_date):
    # print "inside weekly_wet"
    return calc_weekly(user, last_date, next_date, dry=False)


@is_eligible
def calc_weekly(user, last_date, next_date, dry=True):
    # calculate number of weeks passed since last_date before next_date
    # print "for user %s" %(user.username)
    pkg = get_package(user)
    user_doj = pkg.created_at.date()
    num_weeks = 0
    # user_doj = user.date_joined.date()
    # user_doj = date(user_doj.year, user_doj.month, user_doj.day)
    # old_date_time = pkg.created_at if pkg.created_at > last_date else last_date
    old_date_time = greater_date(pkg.created_at, last_date)
    new_date = next_date.date()
    old_date = old_date_time.date()
    if old_date_time < next_date:
        delta = next_date - old_date_time
        num_weeks = floor(delta.days/7.0)
        # pkg = get_package(user)
        # payout = (pkg.package.payout/100.) * pkg.package.price
        # res = (round((payout * num_weeks), 2), 'direct')
        res = payout, _ = calc_daily(user, old_date_time, next_date)
    else:
        res = payout, _ = (0.0, 'direct')
    if num_weeks and dry == False:
        divide_conquer(range(int(num_weeks)), 0, int(num_weeks) - 1,
                       lambda num: gen_txn_weekly(num, old_date, new_date, user, payout))
    return res