# -*- encoding: utf-8 -*-
# [call this script from a3 root with ./bin/python3.4 as interpreter.]
# FIXME: Doesn't work as requests is missing. Use a Python with requests
# installed.

import os
import json
import requests

root_uri = 'http://localhost:6542'
verbose = True

# for more javascript-ish json representation:
null = None
true = True
false = False

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/login_username"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "accept, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

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
    "name": "god",
    "password": "password"
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

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/adhocracy/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8206"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "shady_intelligencesscrawlingMidwaysMurrumbidgee1"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": false,
                    "budget": 16,
                    "other_sources": "hidden treasure",
                    "requested_funding": 29
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_is_specific": true,
                    "location_is_linked_to_ruhr": true,
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "wickerwork Ladonna's preterit's Kyoto's effaced Kenneth's emperor Candy jackknifed expectancy's pursed sultrier overcasts system Eysenck fulfils Bahia newsmen Kinney's Judith's glowworm's chintzier goatees alchemy ingratiated frigate passels Poznan's",
                    "title": "shady intelligence's scrawling Midway's Murrumbidgee1"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "planned_nonprofit",
                    "country": "CC",
                    "website": "http://www.heise.de/http://northscape.net/",
                    "planned_date": "03/01/2015",
                    "name": "nameconstantly"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "NR",
                    "family_name": "fagging",
                    "personal_name": "hypertension Solis"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8261"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "gendarmes_SylviasacquiescingCristinasmantels2"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": false,
                    "budget": 20,
                    "other_sources": "hidden treasure",
                    "requested_funding": 8
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_is_specific": true,
                    "location_specific_3": "location_specific_3",
                    "location_is_linked_to_ruhr": true,
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "silent's yawing nitrate retreaded desalinating electrocutions cheerfulness upchucks cutter's sorrowfully nonwhite's dinner's contrariness whore perching Nantucket's misogyny's Blackburn's model colonialist's sentimentalizing unpalatable lorded",
                    "title": "gendarmes Sylvia's acquiescing Cristina's mantel's2"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "planned_nonprofit",
                    "country": "EC",
                    "website": "http://www.heise.de/http://northscape.net/",
                    "planned_date": "11/01/2017",
                    "name": "nameworrier tortes"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "UG",
                    "family_name": "shleps elastic's",
                    "personal_name": "orange's electrically wieners"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8182"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "frazzles_tripcombinesextensionspyre5"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 26,
                    "other_sources": "hidden treasure",
                    "requested_funding": 25
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_specific_2": "location_specific_2",
                    "location_is_linked_to_ruhr": true,
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "hennaing encoring ideogram's sahib avowing sophist's ditties spas deaconesses Voltaire's Tahitian Moog Adam's appointees Calvin's Amsterdam's strop's organelle's Demavend cogitating homework's cloakroom's reenforces",
                    "title": "frazzles trip combines extensions pyre5"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "planned_nonprofit",
                    "country": "PW",
                    "website": "http://www.heise.de/http://northscape.net/",
                    "planned_date": "01/01/2016",
                    "name": "namesturdiest steadying gyp's"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "AZ",
                    "family_name": "Bologna",
                    "personal_name": "fervid algorithms harkens"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8386"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "incompleteness_pigmentsjawbonesdoggednessBobbi7"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 11,
                    "other_sources": "hidden treasure",
                    "requested_funding": 9
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_is_specific": true,
                    "location_is_online": true,
                    "location_specific_3": "location_specific_3",
                    "location_is_linked_to_ruhr": true,
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "partying pigeonholing Pushkin tousles faintly animate appreciate spare denigration's treadmill jungles",
                    "title": "incompleteness pigments jawbones doggedness Bobbi7"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "other",
                    "status_other": "ordeal drawstrings chattiness supremacy rs spoonerism's schoolmistress's housemaid boons yaws's stancher emerging preconceives reconciled rumbles festival's terrarium dogfight gestate Borneo's nitrate's gelt Damien guttering wooers pointless familiarity written drunkenly tigers",
                    "country": "CC",
                    "website": "http://www.heise.de/",
                    "planned_date": "03/01/2015",
                    "name": "name"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "NI",
                    "family_name": "powder backpedalling",
                    "personal_name": "huffiest particularizing"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8296"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "helmsmen_portersdesalinatingdisconcertedineptly9"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": false,
                    "budget": 15,
                    "other_sources": "hidden treasure",
                    "requested_funding": 22
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_is_online": true,
                    "location_specific_3": "location_specific_3",
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "oblations constipated inheres mendicant's sybarite vibrato's Manfred drier irrelevancies worsen cervices colonial's ordinal's incremented tranquilizer's LBJ's obligates generic IV's lade altruism",
                    "title": "helmsmen porters desalinating disconcerted ineptly9"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "other",
                    "status_other": "Tarkenton fore bobwhites obviated sty Purdue's stress Belushi's labels killings calorific butchers sherds Anatole Svalbard's handkerchiefs Hartline libertarians cheer",
                    "country": "CC",
                    "website": "http://www.heise.de/",
                    "planned_date": "03/01/2015",
                    "name": "name"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "TZ",
                    "family_name": "miscalculated",
                    "personal_name": "decentralization's"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8327"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "overeaten_soughtManciniwheatkith13"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 18,
                    "other_sources": "hidden treasure",
                    "requested_funding": 23
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_specific_3": "location_specific_3",
                    "location_is_linked_to_ruhr": true,
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "Luis Baltic's creams chutzpah lisle flybys relax politico's flagship Spenserian Christmas bedstead thruways Iguassu wronging shirring",
                    "title": "overeaten sought Mancini wheat kith13"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "other",
                    "status_other": "ampersands fisher misogyny's parliamentary agility's Nobelist adopting story's execution's watchfulness's cryptographer's confessions alarmists hashing sublimated indigestion's bondsman Elul's portfolio Manson's Sanchez badmouthing Arabia's constipate discomfited juggle loggerheads",
                    "country": "CC",
                    "website": "http://www.heise.de/",
                    "planned_date": "03/01/2015",
                    "name": "name"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "AQ",
                    "family_name": "roe's Cooperstown's",
                    "personal_name": "perversely"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8225"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "rightful_orthodontiaspickerfivesnonprescription14"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": false,
                    "budget": 2,
                    "other_sources": "hidden treasure",
                    "requested_funding": 24
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_is_specific": true,
                    "location_specific_3": "location_specific_3",
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "spiritualistic combinations text's operative overstep tuns clitorises guarantied smirch's strops hayseed miasmas courtyard's handcuffing canasta's weepies fig Flossie's berm rapping yoghurt's fens Somme's mooring's adulation's Catholicisms",
                    "title": "rightful orthodontia's picker five's nonprescription14"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "planned_nonprofit",
                    "country": "KY",
                    "website": "http://www.heise.de/http://northscape.net/",
                    "planned_date": "03/01/2015",
                    "name": "nameSisyphus"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "ES",
                    "family_name": "thanking offense's",
                    "personal_name": "ticking curtailment Wiemar's"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8154"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "stunned_RoentgenrailroadforbidMarions15"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 6,
                    "other_sources": "hidden treasure",
                    "requested_funding": 11
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_is_specific": true,
                    "location_specific_2": "location_specific_2",
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "mathematician wallabies slovenlier Rhineland noisily balustrade's interpreter Brett obviating Lucknow's Haiphong privation's peonage luxuriating honorably yowled",
                    "title": "stunned Roentgen railroad forbid Marion's15"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "registered_nonprofit",
                    "country": "AU",
                    "website": "http://www.heise.de/http://northscape.net/",
                    "planned_date": "03/01/2015",
                    "name": "nameunappetizing Cretaceous cloudbursts"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "KM",
                    "family_name": "noncooperation's categorization's",
                    "personal_name": "advocated quintuple"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/meta_api"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "GET",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/principals/users/0000000/"
headers = {
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
}
body = ''
response = requests.get(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Access-Control-Request-Headers": "x-user-path, accept, x-user-token, content-type"
}
body = ''
response = requests.options(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "X-User-Token": "677c59c2498168b09e25b3bae931ac13960b06ce67b9fbdd13f2187fe132b7f3e031a63587a72ff4b5330102c65d14ab93e2db6d58ec0569eee0e60aa49c5c10",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip,deflate",
    "Connection": "keep-alive",
    "X-User-Path": "" + root_uri + "/principals/users/0000000/",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
    "Content-Length": "8151"
}
body = json.dumps([
    {
        "path": "" + root_uri + "/mercator/",
        "body": {
            "parent": "" + root_uri + "/mercator/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "deviated_shogunspudgierdeviseddisquiet18"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
            "first_version_path": "@pn32"
        },
        "result_path": "@pn31",
        "method": "POST",
        "result_first_version_path": "@pn32"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Experience"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperience",
            "first_version_path": "@pn29"
        },
        "result_path": "@pn28",
        "method": "POST",
        "result_first_version_path": "@pn29"
    },
    {
        "path": "@pn28",
        "body": {
            "parent": "@pn28",
            "data": {
                "adhocracy_mercator.sheets.mercator.IExperience": {
                    "experience": "experience"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn29"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion"
        },
        "result_path": "@pn30",
        "method": "POST",
        "result_first_version_path": "@pn34"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Finance"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinance",
            "first_version_path": "@pn26"
        },
        "result_path": "@pn25",
        "method": "POST",
        "result_first_version_path": "@pn26"
    },
    {
        "path": "@pn25",
        "body": {
            "parent": "@pn25",
            "data": {
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": false,
                    "budget": 27,
                    "other_sources": "hidden treasure",
                    "requested_funding": 20
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn26"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IFinanceVersion"
        },
        "result_path": "@pn27",
        "method": "POST",
        "result_first_version_path": "@pn35"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartners",
            "first_version_path": "@pn23"
        },
        "result_path": "@pn22",
        "method": "POST",
        "result_first_version_path": "@pn23"
    },
    {
        "path": "@pn22",
        "body": {
            "parent": "@pn22",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn23"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IPartners": {
                    "partners": "partners"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion"
        },
        "result_path": "@pn24",
        "method": "POST",
        "result_first_version_path": "@pn36"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Value"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValue",
            "first_version_path": "@pn20"
        },
        "result_path": "@pn19",
        "method": "POST",
        "result_first_version_path": "@pn20"
    },
    {
        "path": "@pn19",
        "body": {
            "parent": "@pn19",
            "data": {
                "adhocracy_mercator.sheets.mercator.IValue": {
                    "value": "value"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn20"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IValueVersion"
        },
        "result_path": "@pn21",
        "method": "POST",
        "result_first_version_path": "@pn37"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Steps"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.ISteps",
            "first_version_path": "@pn17"
        },
        "result_path": "@pn16",
        "method": "POST",
        "result_first_version_path": "@pn17"
    },
    {
        "path": "@pn16",
        "body": {
            "parent": "@pn16",
            "data": {
                "adhocracy_mercator.sheets.mercator.ISteps": {
                    "steps": "steps"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn17"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion"
        },
        "result_path": "@pn18",
        "method": "POST",
        "result_first_version_path": "@pn38"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcome",
            "first_version_path": "@pn14"
        },
        "result_path": "@pn13",
        "method": "POST",
        "result_first_version_path": "@pn14"
    },
    {
        "path": "@pn13",
        "body": {
            "parent": "@pn13",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn14"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOutcome": {
                    "outcome": "outcome"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion"
        },
        "result_path": "@pn15",
        "method": "POST",
        "result_first_version_path": "@pn39"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStory",
            "first_version_path": "@pn11"
        },
        "result_path": "@pn10",
        "method": "POST",
        "result_first_version_path": "@pn11"
    },
    {
        "path": "@pn10",
        "body": {
            "parent": "@pn10",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn11"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IStory": {
                    "story": "story"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion"
        },
        "result_path": "@pn12",
        "method": "POST",
        "result_first_version_path": "@pn40"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Details"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetails",
            "first_version_path": "@pn8"
        },
        "result_path": "@pn7",
        "method": "POST",
        "result_first_version_path": "@pn8"
    },
    {
        "path": "@pn7",
        "body": {
            "parent": "@pn7",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn8"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_specific_1": "location_specific_1",
                    "location_specific_3": "location_specific_3",
                    "location_specific_2": "location_specific_2",
                    "description": "description"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IDetailsVersion"
        },
        "result_path": "@pn9",
        "method": "POST",
        "result_first_version_path": "@pn41"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "Introduction"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
            "first_version_path": "@pn5"
        },
        "result_path": "@pn4",
        "method": "POST",
        "result_first_version_path": "@pn5"
    },
    {
        "path": "@pn4",
        "body": {
            "parent": "@pn4",
            "data": {
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "braving noshed Aramco helm floury parleyed tippler's gunboats Mantle Hottentot's Darcy Mongolian ruled Arthur's Ptah's colleges swap's portrait's chromes rifer Turkish's Richthofen daydreaming",
                    "title": "deviated shogun's pudgier devised disquiet18"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn5"
                    ]
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IIntroductionVersion"
        },
        "result_path": "@pn6",
        "method": "POST",
        "result_first_version_path": "@pn42"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "OrganizationInfo"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
            "first_version_path": "@pn2"
        },
        "result_path": "@pn1",
        "method": "POST",
        "result_first_version_path": "@pn2"
    },
    {
        "path": "@pn1",
        "body": {
            "parent": "@pn1",
            "data": {
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn2"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "status": "planned_nonprofit",
                    "country": "KY",
                    "website": "http://www.heise.de/http://northscape.net/",
                    "planned_date": "01/01/2016",
                    "name": "namescrods"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn43"
    },
    {
        "path": "@pn31",
        "body": {
            "parent": "@pn31",
            "data": {
                "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                    "heard_elsewhere": ""
                },
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "country": "LK",
                    "family_name": "prolific Mitch's",
                    "personal_name": "sonnies"
                },
                "adhocracy_core.sheets.versions.IVersionable": {
                    "follows": [
                        "@pn32"
                    ]
                },
                "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                    "partners": "@pn24",
                    "finance": "@pn27",
                    "introduction": "@pn6",
                    "value": "@pn21",
                    "steps": "@pn18",
                    "outcome": "@pn15",
                    "organization_info": "@pn3",
                    "details": "@pn9",
                    "story": "@pn12",
                    "experience": "@pn30"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn33",
        "method": "POST",
        "result_first_version_path": "@pn44"
    }
])
response = requests.post(uri, headers=headers, data=body)
if verbose:
    print('\n')
    print(uri)
    print(headers)
    print(body)
    print(response)
    print(response.text)
assert response.status_code == 200
