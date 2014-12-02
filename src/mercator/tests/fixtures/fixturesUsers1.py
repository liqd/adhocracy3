# -*- encoding: utf-8 -*-
# [call this script from a3 root with ./bin/python3.4 as interpreter.]
# FIXME: Doesn't work as requests is missing. Use a Python with requests
# installed.

import os
import json
import requests

root_uri = 'http://lig:6541'
verbose = True

# for more javascript-ish json representation:
null = None
true = True
false = False

def register_user(user_name):
    uri = root_uri + "/principals/users/"
    headers = {
        "X-User-Token": "SECRET_GOD",
        "X-User-Path": "/principals/users/0000000/",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip,deflate",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
        "Content-Length": "238"
        }
    body = json.dumps({
            "data": {
                "adhocracy_core.sheets.principal.IPasswordAuthentication": {
                    "password": "password"
                },
                "adhocracy_core.sheets.principal.IUserBasic": {
                "email": user_name + "@posteo.de",
                "name": user_name
            }
        },
        "content_type": "adhocracy_core.resources.principal.IUser"
    })
    response = requests.post(uri, headers=headers, data=body)
    if verbose:
        print('\n')
        print(uri)
        print(headers)
        print(body)
        print(response)
        print(response.text)

    assert response.status_code == 200


for n in ["carla","cindy","conrad","hanna","joe","kalle","nina","phillip","theo","zoe"]:
    register_user(n + "3")
