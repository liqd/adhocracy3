# -*- encoding: utf-8 -*-
# you can execute this module from $A3_ROOT with ./bin/ipython as interpreter.

import os
import json
import requests
from random import choice
from random import randint

# FIXME: root_uri must be constructed from etc/*.ini, not hard-coded here!
root_uri = 'http://localhost:6541'
verbose = True

# for more javascript-ish json representation:
null = None
true = True
false = False

def headers(length):
    return {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip,deflate",
        "Connection": "keep-alive",
        "X-User-Token": "SECRET_GOD",
        "X-User-Path": "" + root_uri + "/principals/users/0000000/",
        "Accept-Language": "en-US,en;q=0.8",
        "Content-Length": length
    }

pool_resource = {
    'content_type': 'adhocracy_core.resources.asset.IPoolWithAssets',
    'data': {'adhocracy_core.sheets.name.IName': {'name':  'proposals'}}
}

body = json.dumps(pool_resource)
uri = root_uri + "/mercator"
response = requests.post(uri, headers=headers(str(len(body))), data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)

assert response.status_code == 200
