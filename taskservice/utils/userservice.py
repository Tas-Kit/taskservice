import os
import requests

host = os.getenv('USERSERVICE', 'userservice')
base_url = 'http://{0}'
sub_url = '/api/v1/userservice'


def get_user_list(uid_list):
    query = '&'.join(['id={0}'.format(uid) for uid in uid_list])
    url = '{0}{1}/users/?{2}'.format(base_url, sub_url, query)
    response = requests.get(url)
    return response.json()['results']


def get_user(uid):
    url = '{0}{1}/users/?id={2}'.format(base_url, sub_url, uid)
    response = requests.get(url)
    return response.json()['results'][0]
