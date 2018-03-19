# runs one time
import datetime
from pytz import UTC
from avicrypto.settings import EPOCH_BEGIN
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.lib.payout import  get_package, run_scheduler, calculate_investment, run_investment_calc, find_next_monday

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

def reset_these():
    # import pdb
    # for email in ["robertjohnlie@gmail.com", "erwinyap.btc@gmail.com", "lilibest.btc@gmail.com",
    #     "zoulbizz@gmail.com", "andrisaputra148@gmail.com", "masta2803@gmail.com", 
    #     "amirryand8@gmail.com", "suherman6224@gmail.com", "cryptomujur@gmail.com",
    #     "billioner.kaya@gmail.com", "wildareflita1972@gmail.com"]:
    #     u = User.objects.get(email = email)
    #     u.date_joined = UTC.normalize(UTC.localize(datetime.datetime(2018, 2, 1, 00, 00, 00)))
    #     u.set_password("avi123456")
    #     u.save()
    #     pkg = User_packages.objects.filter(user = u, status='A')
    #     if pkg:
    #         pkg = pkg[0]    
    #         pkg.updated_at = u.date_joined
    #         pkg.last_payout_date = u.date_joined
    #         pkg.binary = 0.0
    #         pkg.weekly = 0.0
    #         pkg.direct = 0.0
    #         pkg.total_payout = 0.0
    #         pkg.left_binary_cf = 0.0
    #         pkg.right_binary_cf = 0.0
    #         pkg.save()
    users = User.objects.all()
    for user in users:
        u = user
        # try:
        u.set_password('avi1234')
        u.save()
        # pkg = get_package(u)
        # if pkg:
        #     print "has pkg"
        #     pkg.last_payout_date = EPOCH_BEGIN
        #     pkg.binary = 0.0
        #     pkg.weekly = 0.0
        #     pkg.direct = 0.0
        #     # pkg.total_payout += pkg.weekly
        #     pkg.left_binary_cf = 0.0
        #     pkg.right_binary_cf = 0.0
        #     pkg.save()
        #     # today = UTC.normalize(UTC.localize(datetime.datetime.utcnow()))
        #     # # pdb.set_trace()
        #     admin_param = {
        #         'admin': User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us'),
        #         'start_dt': EPOCH_BEGIN,
        #         'end_dt': UTC.normalize(UTC.localize(datetime.datetime(2018, 03, 12)))
        #     }
        #     # print "calling run_investment_calc(u, pkg, EPOCH_BEGIN, today, **admin_param)"
        #     run_investment_calc(u, pkg, EPOCH_BEGIN, admin_param['end_dt'], **admin_param)
        #     print "called run_investment_calc"

        # except Exception as e:
        #     print "error for", u.username
        #     print "error is", e, e.message
        #     print Exception(e)
        #     pass
    # print "running"
    # # print run_scheduler()
    # for u in users:
    #     pkg = User_packages.objects.filter(user = u, status='A')
    #     if pkg:
    #         pkg = pkg[0]
    #         # calculate_investment(u)
    #         # # pkg.total_payout = pkg.weekly
    #         # pkg.save()
    # print "run_scheduler() done"


class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        reset_these()
        self.stdout.write(self.style.SUCCESS('Successfully reset'))