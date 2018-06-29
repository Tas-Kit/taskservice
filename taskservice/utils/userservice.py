import os
import requests

host = os.getenv('USERSERVICE', 'userservice')
base_url = 'http://{0}:8000'.format(host)
sub_url = '/api/v1/userservice'


def get_user_list(uid_list):
    if uid_list:
        query = '&'.join(['id={0}'.format(uid) for uid in uid_list])
        url = '{0}{1}/users/?{2}'.format(base_url, sub_url, query)
        response = requests.get(url)
        return response.json()['results']
    return []


def get_user(uid=None, username=None):
    query = []
    if uid:
        query.append('uid={0}'.format(uid))
    if username:
        query.append('username={0}'.format(username))
    if query:
        url = '{0}{1}/users/?{2}'.format(base_url, sub_url, '&'.join(query))
        response = requests.get(url)
        return response.json()['results'][0]
    return []
