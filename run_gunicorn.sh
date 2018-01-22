#!/bin/bash

WORKERS=6
WORKER_CLASS="gevent"
PORT=5582

gunicorn --bind 0.0.0.0:${PORT} \
-w ${WORKERS} -k ${WORKER_CLASS} \
--reload wsgi:app --access-logfile -
