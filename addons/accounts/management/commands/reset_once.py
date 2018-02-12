# runs one time
import datetime
from pytz import UTC
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.packages.lib.payout import run_scheduler, calculate_investment

from django.core.management.base import BaseCommand, CommandError

def reset_these():    
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

    # users = User.objects.all()
    # for u in users:
    #     pkg = User_packages.objects.filter(user = u, status='A')
    #     if pkg:
    #         pkg = pkg[0]
    #         # pkg.last_payout_date = u.date_joined
    #         # pkg.binary = 0.0
    #         # pkg.weekly = 0.0
    #         # pkg.direct = 0.0
    #         pkg.total_payout = pkg.weekly
    #         # pkg.left_binary_cf = 0.0
    #         # pkg.right_binary_cf = 0.0
    #         pkg.save()
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
    u = User.objects.get(username="AVI000000100")
    pkg = User_packages.objects.get(user = u)
    calculate_investment(u)
    


class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        reset_these()
        self.stdout.write(self.style.SUCCESS('Successfully reset'))