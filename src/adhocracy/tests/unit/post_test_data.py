#!/usr/bin/python3

from os import path
import json
import os
import sys

# FIXME Is there a cleaner way to do this?
eggs_dir = path.normpath(path.join(path.dirname(path.realpath(__file__)), '../../../../eggs'))
sys.path[0:0] = [
    path.join(eggs_dir, 'requests-2.1.0-py3.3.egg')
]

import requests

if 'A3_TEST_SERVER' in os.environ and os.environ['A3_TEST_SERVER']:
    server = os.environ['A3_TEST_SERVER'].rstrip('/')
else:
    server = "http://localhost:6541"


def _print_request(data: str, uri: str, method: str='post') -> None:
    print('====================================================================== [REQUEST]')
    print('  method: ' + method)
    print('  uri: ' + uri)
    print('  data: ' + data)
    print('')


def _print_response_or_give_up(response: requests.Response) -> None:
    print('---------------------------------------------------------------------- [RESPONSE]')
    print('  code: ' + str(response.status_code))
    if response.status_code == 200:
        print('  data: ' + json.dumps(response.json()))
        print('')
    else:
        print('  data: ' + response.text)
        print('')
        print('giving up!')
        exit(1)


def _post_data(path: str, request_dict: dict) -> dict:
    """"Post a JSON object to the server and return the response dictionary.

    Also prints the request and the resulting response for easy visual feedback.
    Gives up and exists the app if the server responds with an error.
    """
    data = json.dumps(request_dict)
    uri = server + path
    _print_request(data, uri, method='post')
    response = requests.post(uri, data=data,
                             headers={'content-type': 'text/json',})
    _print_response_or_give_up(response)
    return response.json()


# Create Proposals pool
resp = _post_data('/adhocracy/',
                  {'content_type': 'adhocracy.resources.pool.IBasicPool',
                    'data': {
                         'adhocracy.sheets.name.IName': {
                             'name': 'Proposals'}}})

# Add kommunismus IProposal to Proposals pool
resp = _post_data('/adhocracy/Proposals',
                  {'content_type': 'adhocracy_sample.resources.proposal.IProposal',
                   'data': {
                        'adhocracy.sheets.name.IName': {
                            'name': 'kommunismus'}
                        }
                  })
first_proposal_version = resp['first_version_path']

# Ad another (non-empty) proposal version
resp = _post_data('/adhocracy/Proposals/kommunismus',
                  {'content_type': 'adhocracy_sample.resources.proposal.IProposalVersion',
                   'data': {'adhocracy.sheets.document.IDocument': {
                               'title': 'kommunismus jetzt!',
                               'description': 'blabla!',
                               'elements': []},
                            'adhocracy.sheets.versions.IVersionable': {
                               'follows': [first_proposal_version]}},
                    'root_versions': [first_proposal_version]})
second_proposal_version = resp['path']

# Add two sections to the kommunismus proposal
resp = _post_data('/adhocracy/Proposals/kommunismus',
           {'content_type': 'adhocracy_sample.resources.section.ISection',
             'data': {'adhocracy.sheets.name.IName': {'name': 'kapitel1'}}})
first_sec1_version = resp['first_version_path']

resp = _post_data('/adhocracy/Proposals/kommunismus',
                  {'content_type': 'adhocracy_sample.resources.section.ISection',
                    'data': {'adhocracy.sheets.name.IName': {'name': 'kapitel2'}}})
first_sec2_version = resp['first_version_path']

# Add the initial versions of these sections to a third version of the proposal
resp = _post_data('/adhocracy/Proposals/kommunismus',
                  {'content_type': 'adhocracy_sample.resources.proposal.IProposalVersion',
                   'data': {'adhocracy.sheets.document.IDocument': {
                                'elements': [first_sec1_version, first_sec2_version]},
                            'adhocracy.sheets.versions.IVersionable': {
                                'follows': [second_proposal_version],}
                            },
                     'root_versions': [second_proposal_version]})

# TODO from l.582

# TODO Old stuff
exit(0)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IProposalContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + rootpath)
print('  data: ' + data)
resp_0 = requests.post(server + rootpath, data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_0.status_code))
if resp_0.status_code == 200:
    print('  data: ' + json.dumps(resp_0.json()))
    print('')

else:
    print('  data: ' + resp_0.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {
        "adhocracy.propertysheets.interfaces.IDocument": {
            "paragraphs": [],
            "title": "Der Käpt'n",
            "description": "von Peter Maria Neuhaus (titanic 9/2012)"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IProposal"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_1 = requests.post(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_1.status_code))
if resp_1.status_code == 200:
    print('  data: ' + json.dumps(resp_1.json()))
    print('')

else:
    print('  data: ' + resp_1.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IProposalContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + rootpath)
print('  data: ' + data)
resp_2 = requests.post(server + rootpath, data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_2.status_code))
if resp_2.status_code == 200:
    print('  data: ' + json.dumps(resp_2.json()))
    print('')

else:
    print('  data: ' + resp_2.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IProposalContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + rootpath)
print('  data: ' + data)
resp_3 = requests.post(server + rootpath, data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_3.status_code))
if resp_3.status_code == 200:
    print('  data: ' + json.dumps(resp_3.json()))
    print('')

else:
    print('  data: ' + resp_3.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_4 = requests.post(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_4.status_code))
if resp_4.status_code == 200:
    print('  data: ' + json.dumps(resp_4.json()))
    print('')

else:
    print('  data: ' + resp_4.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_5 = requests.post(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_5.status_code))
if resp_5.status_code == 200:
    print('  data: ' + json.dumps(resp_5.json()))
    print('')

else:
    print('  data: ' + resp_5.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_6 = requests.post(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_6.status_code))
if resp_6.status_code == 200:
    print('  data: ' + json.dumps(resp_6.json()))
    print('')

else:
    print('  data: ' + resp_6.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_7 = requests.post(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_7.status_code))
if resp_7.status_code == 200:
    print('  data: ' + json.dumps(resp_7.json()))
    print('')

else:
    print('  data: ' + resp_7.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraph"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_4.json()['path'])
print('  data: ' + data)
resp_8 = requests.post(server + resp_4.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_8.status_code))
if resp_8.status_code == 200:
    print('  data: ' + json.dumps(resp_8.json()))
    print('')

else:
    print('  data: ' + resp_8.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "Schwach ist sein Gang, mit kurzen Trippelschrittchen\nvom Heck zum Kiel, seniorenhaft verdreht.\nQuecksilberfischig jedes zweite Trittchen,\nweil er auf einem Narwal-Holzbein geht.\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_5.json()['path'])
print('  data: ' + data)
resp_10 = requests.post(server + resp_5.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_10.status_code))
if resp_10.status_code == 200:
    print('  data: ' + json.dumps(resp_10.json()))
    print('')

else:
    print('  data: ' + resp_10.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "Nur einmal schiebt der Vorhang vom Pupillchen\nsich auf: Europa retten kann nur er!\nStark wie ein Wal war früher ja sein Willchen.\nDoch heute? Käpt’n Iglo bläst nicht mehr.\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_6.json()['path'])
print('  data: ' + data)
resp_11 = requests.post(server + resp_6.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_11.status_code))
if resp_11.status_code == 200:
    print('  data: ' + json.dumps(resp_11.json()))
    print('')

else:
    print('  data: ' + resp_11.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "...\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_7.json()['path'])
print('  data: ' + data)
resp_12 = requests.post(server + resp_7.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_12.status_code))
if resp_12.status_code == 200:
    print('  data: ' + json.dumps(resp_12.json()))
    print('')

else:
    print('  data: ' + resp_12.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {
        "adhocracy.propertysheets.interfaces.IDocument": {
            "paragraphs": [
                {
                    "path": resp_8.json()['path'],
                    "content_type": "adhocracy.contents.interfaces.IParagraph",
                    "reference_colour": "EssenceRef"
                },
                {
                    "path": resp_10.json()['path'],
                    "content_type": "adhocracy.contents.interfaces.IParagraph",
                    "reference_colour": "EssenceRef"
                },
                {
                    "path": resp_11.json()['path'],
                    "content_type": "adhocracy.contents.interfaces.IParagraph",
                    "reference_colour": "EssenceRef"
                },
                {
                    "path": resp_12.json()['path'],
                    "content_type": "adhocracy.contents.interfaces.IParagraph",
                    "reference_colour": "EssenceRef"
                }
            ],
            "title": "Der Käpt'n",
            "description": "von Peter Maria Neuhaus (titanic 9/2012)"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IProposal"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_13 = requests.post(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',    'follows': resp_1.json()['path'],})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_13.status_code))
if resp_13.status_code == 200:
    print('  data: ' + json.dumps(resp_13.json()))
    print('')

else:
    print('  data: ' + resp_13.text)
    print('')
    print('giving up!')
    exit(1)

data = json.dumps({
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "Sein Bart ist vom Vorüberziehn der Stäbchen\nganz weiß geworden, so wie nicht mehr frisch.\nIhm ist, als wenn es tausend Stäbchen gäbchen\nund in den tausend Stäbchen keinen Fisch.\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
})
print('====================================================================== [REQUEST]')
print('  method: ' + 'post')
print('  uri: ' + server + resp_4.json()['path'])
print('  data: ' + data)
resp_19 = requests.post(server + resp_4.json()['path'], data=data, headers={'content-type': 'text/json',    'follows': resp_8.json()['path'],})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_19.status_code))
if resp_19.status_code == 200:
    print('  data: ' + json.dumps(resp_19.json()))
    print('')

else:
    print('  data: ' + resp_19.text)
    print('')
    print('giving up!')
    exit(1)

data = ''
print('====================================================================== [REQUEST]')
print('  method: ' + 'get')
print('  uri: ' + server + resp_0.json()['path'])
print('  data: ' + data)
resp_21 = requests.get(server + resp_0.json()['path'], data=data, headers={'content-type': 'text/json',})
print('')

print('---------------------------------------------------------------------- [RESPONSE]')
print('  code: ' + str(resp_21.status_code))
if resp_21.status_code == 200:
    print('  data: ' + json.dumps(resp_21.json()))
    print('')

else:
    print('  data: ' + resp_21.text)
    print('')
    print('giving up!')
    exit(1)


print('success!')
