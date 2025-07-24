#!/bin/bash

set -e # immediately exit if any fail

# make slave db (source of truth is in supabase)
alembic upgrade head

exec gunicorn --bind 0.0.0.0:8080 -k uvicorn_worker.UvicornWorker app.main:app --proxy_allow_ips "*" --forwarded_allow_ips "*"