"""
Run the background scheduler to schedule a job
"""

from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler
from addons.packages.models import Packages, User_packages
from addons.packages.lib.payout import calc, calculate_investment
from addons.accounts.lib.tree import divide_conquer
from addons.accounts.models import User, Members

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='sun', hour=23)
def tick():
    print('Tick Running. The time is: %s' % datetime.now())
    users = User.objects.all
    divide_conquer(users, 0, len(users), calculate_investment)

if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(tick, 'interval', seconds=3)
    sched.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()