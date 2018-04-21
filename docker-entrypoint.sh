#!/bin/bash
./wait_for_it.sh proxyserver:8000 -- echo "Postgres is up."

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000