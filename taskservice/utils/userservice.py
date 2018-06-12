import os
import requests

host = os.getenv('USERSERVICE', 'userservice')
base_url = 'http://{0}'.format(host)
sub_url = '/api/v1/userservice'


def get_user_list(uid_list):
    query = '&'.join(['id={0}'.format(uid) for uid in uid_list])
    url = '{0}{1}/users/?{2}'.format(base_url, sub_url, query)
    response = requests.get(url)
    return response.json()['results']


def get_user(uid=None, username=None):
    query = []
    if uid:
        query.append('id={0}'.format(uid))
    if username:
        query.append('username={1}'.format(username))
    url = '{0}{1}/users/?{2}'.format(base_url, sub_url, '&'.join(query))
    response = requests.get(url)
    return response.json()['results'][0]
