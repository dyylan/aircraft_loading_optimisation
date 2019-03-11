#!/bin/sh

source venv/bin/activate
exec gunicorn --worker-class gevent --workers 3 -b :5000 --access-logfile - --error-logfile - main:app