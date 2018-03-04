from addons.packages.models import Packages, User_packages
from django.core.management.base import BaseCommand, CommandError
from addons.packages.lib.payout import run_scheduler
from itertools import chain
from django.utils import timezone
from django.contrib.auth.models import User
from addons.accounts.models import Members, Profile, SupportTicket, UserAccount

class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        for profile in profiles:
            # print profile

            if profile.referal_code or profile.sponser_id:
                if profile.sponser_id:
                    profile.referal_code = profile.sponser_id.profile.my_referal_code
                    profile.save()

        # user_packages =  User_packages.objects.all()

        # for user_package in user_packages:
        #     user_package.last_direct_binary_date = user_package.last_payout_date
        #     user_package.save()

        self.stdout.write(self.style.SUCCESS('Set Binary Direct Last Payout Date'))