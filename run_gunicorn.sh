#!/bin/bash

WORKERS=4
# WORKER_CLASS="gevent"
WORKER_CLASS="sync"
PORT=5582

cd /home/ec2-user/projects/slm_histviz
.venv/bin/gunicorn \
--bind 0.0.0.0:${PORT} \
-w ${WORKERS} -k ${WORKER_CLASS} \
--reload wsgi:app --access-logfile -
