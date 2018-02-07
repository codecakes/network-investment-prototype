import django_rq
from datetime import timedelta, datetime
import os

worker = django_rq.get_worker('crypto_payments') # Returns a worker for "low" and "high"

if __name__ == '__main__':
    worker.work()