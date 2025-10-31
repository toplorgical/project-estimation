#!/bin/sh
set -e

# Initialize app (migrate, ensure superuser, seed sample data once)
python manage.py init_app

# Execute the main process (gunicorn by default via CMD)
exec "$@"
