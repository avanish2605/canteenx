#!/usr/bin/env bash
# Exit immediately on error
set -o errexit

# 1. Install production dependencies
pip install -r requirements.txt

# 2. Collect static files for WhiteNoise
python manage.py collectstatic --no-input

# 3. Apply database migrations
python manage.py migrate

# 4. Seed initial university canteen data (safe to run multiple times)
python manage.py create_initial_data
