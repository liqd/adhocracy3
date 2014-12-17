# -*- encoding: utf-8 -*-
# [call this script from a3 root with ./bin/python3.4 as interpreter.]
# FIXME: Doesn't work as requests is missing. Use a Python with requests
# installed.

import json
import os
import re
import requests

email_spool_path = os.environ['A3_ROOT'] + '/var/mail/new/'
LOG_PATH = os.environ['A3_ROOT'] + '/var/log/test_adhocracy_backend.log'
root_uri = 'http://localhost:6542'
verbose = True

# for more javascript-ish json representation:
null = None
true = True
false = False


def register_user(user_name, password='password'):
    uri = root_uri + '/principals/users/'
    body = json.dumps({
            'data': {
                'adhocracy_core.sheets.principal.IPasswordAuthentication': {
                    'password': password
                },
                'adhocracy_core.sheets.principal.IUserBasic': {
                'email': user_name + '@example.org',
                'name': user_name
                }
            },
            'content_type': 'adhocracy_core.resources.principal.IUser'
    })
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip,deflate',
        'Connection': 'keep-alive',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
        'Content-Length': str(len(body))
        }
    response = requests.post(uri, headers=headers, data=body)
    if verbose:
        print('\n')
        print(uri)
        print(headers)
        print(body)
        print(response)
        print(response.text)

    return response.status_code == 200


def activate_account(path):
    uri = root_uri + '/activate_account'
    body = json.dumps({
        'path': path
    })
    headers = {
        'X-User-Token': 'SECRET_GOD',
        'X-User-Path': '/principals/users/0000000/',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'en-US,en;q=0.8,de;q=0.6',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
        'Content-Length': len(body)
    }
    response = requests.post(uri, headers=headers, data=body)
    if verbose:
        print('\n')
        print(uri)
        print(headers)
        print(body)
        print(response)
        print(response.text)

    return response.status_code == 200

def get_activation_path(name):
    with open(LOG_PATH, 'r') as f:
        file_contents = f.read()[-256:]

    pattern = re.compile('user named %s, activation path=/activate/.*' % name)
    match = pattern.search(file_contents)
    if match is not None:
        return match.group(0)[-34:]

    print('*** no match in file: ' + LOG_PATH)
    return None

def create_user(name, password='password'):
    if not register_user(name, password):
        print('*** failed to register user')
    path = get_activation_path(name)
    activate_account(path)

if __name__ == "__main__":
    for n in ['carla','cindy','conrad','hanna','joe','kalle','nina','phillip','theo','zoe']:
        register_user(n + "")
    activate_all()
