# runs one time
import datetime
from pytz import UTC
from django.conf import settings
EPOCH_BEGIN = settings.EPOCH_BEGIN
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.lib.payout import  get_package, run_scheduler, calculate_investment, run_investment_calc, find_next_monday

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

def reset_these():
    users = User.objects.all()
    for user in users:
        u = user
        # try:
        # u.set_password('avi1234')
        # u.save()
        pkg = get_package(u)
        if pkg:
            # print "has pkg"
            pkg.last_payout_date = EPOCH_BEGIN
            pkg.binary = 0.0
            pkg.weekly = 0.0
            pkg.direct = 0.0
            # pkg.total_payout += pkg.weekly
            pkg.left_binary_cf = 0.0
            pkg.right_binary_cf = 0.0
            pkg.save()
            # today = UTC.normalize(UTC.localize(datetime.datetime.utcnow()))
            # # pdb.set_trace()
            admin_param = {
                'admin': User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us'),
                'start_dt': EPOCH_BEGIN,
                'end_dt': UTC.normalize(UTC.localize(datetime.datetime(2018, 3, 28)))
            }
            # print "calling run_investment_calc(u, pkg, EPOCH_BEGIN, today, **admin_param)"
            run_investment_calc(u, pkg, EPOCH_BEGIN, admin_param['end_dt'], **admin_param)
            # print "called run_investment_calc"
        # except Exception as e:
        #     print "error for", u.username
        #     print "error is", e, e.message
        #     print Exception(e)
        #     pass


class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        reset_these()
        self.stdout.write(self.style.SUCCESS('Successfully reset'))