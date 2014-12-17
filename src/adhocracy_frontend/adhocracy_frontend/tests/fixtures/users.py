# -*- encoding: utf-8 -*-
# you can execute this module from $A3_ROOT with ./bin/ipython as interpreter.

import json
import os
import re
import requests

email_spool_path = os.environ['A3_ROOT'] + '/var/mail/new/'
root_uri = 'http://localhost:6541'
verbose = True

# for more javascript-ish json representation:
null = None
true = True
false = False

def register_user(user_name, password="password"):
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

    assert response.status_code == 200


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

    #assert response.status_code == 200

def activate_all():
    for file in glob.glob(email_spool_path + "*"):
        file_contents = open(file, 'r').read()

        m = re.search('https?://.*(/activate/.*)', file_contents)
        if m is not None:
            activate_account(m.group(1))
        else:
            print("*** no match in file: " + file)

if __name__ == "__main__":
    for n in ['carla','cindy','conrad','hanna','joe','kalle','nina','phillip','theo','zoe']:
        register_user(n + "")
    activate_all()
