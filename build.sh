#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
python manage.py migrate auth
python manage.py migrate admin
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate users
python manage.py migrate tasks
python manage.py migrate home
python manage.py migrate community

# Collect static files
python manage.py collectstatic --no-input 