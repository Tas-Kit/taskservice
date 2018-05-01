import os
from py2neo import Graph
from taskservice.settings.basic import *

DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']

# X_FRAME_OPTIONS = 'DENY'
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 1
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'HOST': 'psqldb',
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'PORT': 5432,
    }
}

NEO4J_AUTH = os.environ['NEO4J_AUTH']
NEO4J_PASS = NEO4J_AUTH.split(':')[1]

NEOMODEL_NEO4J_BOLT_URL = 'bolt://{0}@neo4jdb:7687'.format(NEO4J_AUTH)
neo4jdb = Graph("bolt://neo4jdb:7687", auth=('neo4j', NEO4J_PASS), password=NEO4J_PASS)

URLS = {
    'auth': 'http://authserver:8000/',
    'base': 'https://sandbox.tas-kit.com/',
    'main': 'https://sandbox.tas-kit.com/main/'
}
