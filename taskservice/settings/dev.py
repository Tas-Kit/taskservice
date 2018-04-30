from taskservice.settings.basic import *
from py2neo import Graph

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4en5-g!mfyx*qipadkt2fmowkyt-fj&4%qx#a#td4&b$58_@)9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

NEOMODEL_NEO4J_BOLT_URL = 'bolt://neo4j:neo4jpass@neo4jdb:7687'
neo4jdb = Graph("bolt://neo4jdb:7687", auth=('neo4j', 'neo4jpass'), password='neo4jpass')
