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
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title0"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title0"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title1"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title1"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title2"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title2"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title3"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title3"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title4"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title4"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title5"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title5"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title6"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title6"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title7"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title7"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title8"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title8"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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

uri = root_uri + "/meta_api"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "0"
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

uri = root_uri + "/batch"
headers = {
    "Content-Type": "application/json",
    "X-User-Token": "SECRET_GOD",
    "X-User-Path": "/principals/users/0000000/",
    "Content-length": "1538"
}
body = json.dumps([
    {
        "path": root_uri + "/adhocracy/",
        "body": {
            "parent": root_uri + "/adhocracy/",
            "data": {
                "adhocracy_core.sheets.name.IName": {
                    "name": "title9"
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
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
                "adhocracy_mercator.sheets.mercator.IUserInfo": {
                    "email": "name.lastname@domain.com",
                    "family_name": "lastname",
                    "personal_name": "name"
                },
                "adhocracy_mercator.sheets.mercator.IDetails": {
                    "location_is_linked_to_ruhr": true,
                    "location_is_city": true,
                    "story": "story",
                    "description": "description"
                },
                "adhocracy_mercator.sheets.mercator.IExtras": {
                    "heard_from_colleague": true,
                    "experience": "experience"
                },
                "adhocracy_mercator.sheets.mercator.IMotivation": {
                    "partners": "partners",
                    "value": "relevance",
                    "steps": "plan",
                    "outcome": "success"
                },
                "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                    "email": "info@domain.com",
                    "status": "registered_nonprofit",
                    "size": "0+",
                    "country": "DE",
                    "name": "organisation name",
                    "city": "city",
                    "postcode": "12345",
                    "street_address": "address",
                    "description": "about"
                },
                "adhocracy_mercator.sheets.mercator.IIntroduction": {
                    "teaser": "teaser",
                    "title": "title9"
                },
                "adhocracy_mercator.sheets.mercator.IFinance": {
                    "granted": true,
                    "budget": 3,
                    "requested_funding": 3
                }
            },
            "root_versions": [],
            "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion"
        },
        "result_path": "@pn3",
        "method": "POST",
        "result_first_version_path": "@pn4"
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
