"""
Run the background scheduler to schedule a job
"""

from datetime import datetime
import time
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avicrypto.settings')

from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()


@sched.scheduled_job('cron', day_of_week='sun', hour=23)
def tick():
    from addons.packages.lib.payout import run_scheduler
    print('Tick Running. The time is: %s' % datetime.now())
    run_scheduler()

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
        sched.shutdown()