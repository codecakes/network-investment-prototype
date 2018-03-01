import datetime
from pytz import UTC
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.packages.lib.payout import run_scheduler, calculate_investment, run_investment_calc, find_next_monday

from django.core.management.base import BaseCommand, CommandError

from addons.packages.lib.payout import run_scheduler


class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        run_scheduler()
        self.stdout.write(self.style.SUCCESS('Run Payout Scheduler'))