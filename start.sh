#!/bin/bash

set -e # immediately exit if any fail

# make slave db (source of truth is in supabase)
python create_dev_db.py

exec gunicorn --bind 0.0.0.0:8080 -k uvicorn_worker.UvicornWorker app.main:app