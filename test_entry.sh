# pylint --load-plugins pylint_django task

coverage run manage.py test -v 2 
coverage html
