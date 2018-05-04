#!/bin/bash
./wait_for_it.sh proxyserver:8000 -- echo "Postgres is up."

# Start server
echo "Starting server"
./manage.py install_labels
./manage.py makemigrations
./manage.py migrate
./manage.py runserver 0.0.0.0:8000