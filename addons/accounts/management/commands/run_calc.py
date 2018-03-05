import datetime
from pytz import UTC
from avicrypto.settings import EPOCH_BEGIN
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.accounts.lib.tree import divide_conquer
from addons.packages.lib.payout import INVESTMENT_TYPE, calc_weekly, run_scheduler, get_package, calculate_investment, run_investment_calc, find_next_monday
from avicrypto.lib.dsm import StateMachine

from django.core.management.base import BaseCommand, CommandError

from addons.packages.lib.payout import run_scheduler

def foo(user, dt):
    pkg = get_package(user)
    if pkg:
        # pkg.last_payout_date = EPOCH_BEGIN
        # pkg.binary = 0.0
        # pkg.weekly = 0.0
        # pkg.direct = 0.0
        # pkg.total_payout = 0.0
        # pkg.left_binary_cf = 0.0
        # pkg.right_binary_cf = 0.0
        # pkg.save()
        doj = pkg.created_at
        if not (doj >= dt):    
            weekly, _ = calc_weekly(user, doj, dt)        
            # run_investment_calc(user, pkg, pkg.last_payout_date, dt)
            # pkg = get_package(user)
            state_m = StateMachine(user)
            state_m.add_state('weekly', INVESTMENT_TYPE, end_state='direct')
            state_m.add_state('direct', INVESTMENT_TYPE, end_state='binary')
            state_m.add_state('binary', INVESTMENT_TYPE, end_state='end')
            # state_m.add_state('loyalty', INVESTMENT_TYPE, end_state='loyalty_booter')
            # state_m.add_state('loyalty_booter', INVESTMENT_TYPE, end_state='loyalty_booter_super')
            # state_m.add_state('loyalty_booter_super', INVESTMENT_TYPE, end_state='end')
            # print "end states:", state_m.end_states
            state_m.set_start('weekly')
            state_m.run(pkg.last_payout_date, dt)
            state_m.set_start('direct')
            state_m.run(pkg.last_payout_date, dt)
            state_m.set_start('binary')
            state_m.run(pkg.last_payout_date, dt)

            # print state_m.results
            binary, left_binary_cf, right_binary_cf = state_m.results['binary']
            direct = state_m.results['direct']
            weekly = state_m.results['weekly']

            pkg.binary = binary
            pkg.left_binary_cf = left_binary_cf
            pkg.right_binary_cf = right_binary_cf
            pkg.direct = direct
            pkg.weekly = weekly
            pkg.total_payout += binary + direct + weekly
            pkg.last_payout_date = find_next_monday()
            pkg.save()
            print "pkg.weekly is %s and weekly is %s" %(pkg.weekly, weekly)
            # pkg.total_payout = pkg.total_payout - pkg.weekly + weekly
            pkg.save()
class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        dt = datetime.datetime(2018, 03, 05, 00, 00, 00, 00)
        dt = UTC.normalize(UTC.localize(dt))
        users = User.objects.all()
        [foo(user, dt) for user in users]
        # divide_conquer(users, 0, len(users)-1, lambda user: self.foo(user, dt))
        # run_scheduler(**{'next_date': dt})
        self.stdout.write(self.style.SUCCESS('Running Payout Scheduler Completed\n'))