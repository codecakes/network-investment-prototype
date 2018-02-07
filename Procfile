release: python manage.py migrate
web: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn avicrypto.wsgi -w 5 --log-file -
clock: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python clock.py
worker: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python run_worker.py