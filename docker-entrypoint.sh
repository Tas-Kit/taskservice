#!/bin/bash
./wait_for_it.sh proxyserver:8000 -- echo "Proxyserver is up."

# Start server
echo "Starting server"
./manage.py install_labels
./manage.py makemigrations
./manage.py migrate
./manage.py makemigrations rest_framework_tracking
./manage.py migrate rest_framework_tracking --database user_log
./manage.py runserver 0.0.0.0:8000
