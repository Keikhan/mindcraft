#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Running migrations..."
# Create database tables for auth and admin
python manage.py migrate auth zero
python manage.py migrate admin zero
python manage.py migrate contenttypes zero
python manage.py migrate sessions zero

# Now run all migrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build completed!" 