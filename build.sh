#!/usr/bin/env bash
set -e

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py makemigrations

python manage.py migrate

python manage.py create_admin

# redeploy-2026-05-25_10-17
