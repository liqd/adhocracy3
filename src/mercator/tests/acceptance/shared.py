"""Shared acceptance test functions that bypass the frontend."""

import requests
import json

from adhocracy_core.testing import god_login
from adhocracy_core.testing import god_password

# FIXME: root_uri must be constructed from etc/*.ini, not hard-coded here!
root_uri = 'http://localhost:6542'
verbose = False

def login(name_or_email, password):
    """login user and return user token """

    uri = root_uri + "/login_username"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip,deflate",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
        "Content-Length": "36"
    }
    body = json.dumps({
        "name": name_or_email,
        "password": password
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

    payload = json.loads(response.text)
    assert payload["status"] == "success"

    return payload["user_token"]

def login_god():
    return login(god_login, god_password)
