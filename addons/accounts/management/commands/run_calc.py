import datetime
from pytz import UTC
from avicrypto.settings import EPOCH_BEGIN
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.accounts.lib.tree import divide_conquer
from addons.packages.lib.payout import run_scheduler, get_package, calculate_investment, run_investment_calc, find_next_monday

from django.core.management.base import BaseCommand, CommandError

from addons.packages.lib.payout import run_scheduler

def foo(user, dt):
    pkg = get_package(user)
    if pkg:    
        pkg.last_payout_date = EPOCH_BEGIN
        pkg.binary = 0.0
        pkg.weekly = 0.0
        pkg.direct = 0.0
        pkg.total_payout = 0.0
        pkg.left_binary_cf = 0.0
        pkg.right_binary_cf = 0.0
        pkg.save()
        run_investment_calc(user, pkg, EPOCH_BEGIN, dt)

class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        dt = datetime.datetime(2018, 02, 26, 00, 00, 00, 00)
        dt = UTC.normalize(UTC.localize(dt))
        users = User.objects.all()
        [foo(user, dt) for user in users]
        # divide_conquer(users, 0, len(users)-1, lambda user: self.foo(user, dt))
        # run_scheduler(**{'next_date': dt})
        self.stdout.write(self.style.SUCCESS('Run Payout Scheduler'))