"""
Run the background scheduler to schedule a job
"""

from datetime import datetime
import time
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avicrypto.settings')

from apscheduler.schedulers.background import BackgroundScheduler

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import django_rq

REDIS_CONN = django_rq.get_connection('crypto_payments')
Q = django_rq.get_queue('crypto_payments', autocommit=True, async=True)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', day_of_week='sun', hour=23)
def tick():
    from addons.packages.lib.payout import run_scheduler
    print('Tick Running. The time is: %s' % datetime.now())
    run_scheduler()


def send_mail_results(job_id):
    from avicrypto.services import send_email_results
    job = Q.fetch_job(job_id)
    result = job.result
    addr = job.meta['addr']
    amt = job.meta['amt']
    send_email_results(amt, addr, result)
    

@sched.scheduled_job('interval', minutes=2)
def run_crypto_worker():
    """Emails results of transaction's varification status used to buy package"""
    from addons.accounts.lib.tree import divide_conquer
    enqueued_ids = Q.job_ids
    divide_conquer(enqueued_ids, 0, len(enqueued_ids)-1, send_mail_results)


if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(tick, 'interval', seconds=3)
    sched.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        # while True:
        #     time.sleep(0.5)
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        sched.shutdown()