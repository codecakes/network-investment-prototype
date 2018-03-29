from functools import wraps
from datetime import timedelta, datetime
import calendar
from pytz import UTC
from payout_aux import get_package
from gen_txn import gen_txn_direct


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


def greater_date(dt1, dt2):
    return max(dt1, dt2)


def find_next_monday():
    """Finds next monday payout date"""
    cur_dt = UTC.normalize(UTC.localize(datetime.utcnow()))
    day = calendar.weekday(cur_dt.year, cur_dt.month, cur_dt.day)
    remaining_days = (7 - day) % 7
    dt = datetime(cur_dt.year, cur_dt.month, cur_dt.day, cur_dt.hour,
                  cur_dt.minute, cur_dt.second, cur_dt.microsecond)
    rem_dt = timedelta(days=remaining_days)
    return UTC.normalize(UTC.localize(dt + rem_dt)) if remaining_days != 0 else UTC.normalize(UTC.localize(dt + timedelta(days=7)))




# filter functions
def filter_by_sponsor(sponsor_id, last_date, next_date, members, dry=True):
    # print "filter_by_sponsor members ", members
    return [m for m in members if valid_payout_user(sponsor_id, m, last_date, next_date, dry=dry)]


@gen_txn_direct
def valid_payout_user(sponsor_id, member, last_date, next_date, dry=True):
    """Filter users that have their Date of Joining between last payout and next payout day
    - params:
        dry: For dry run, no side-effect function if True. If False, generates a Direct Type Transaction. Defaults to True.
    """
    doj = UTC.normalize(member.child_id.date_joined)
    # check if member is active
    pkg = get_package(member.child_id)
    # check if member falls within this cycle.
    # check if is a direct sponsor
    try:
        return (last_date <= doj < next_date) and (member.child_id.profile.sponser_id.profile.user_auto_id == sponsor_id) and pkg
    except:
        return False