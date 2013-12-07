#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import json
import requests

if 'A3_TEST_SERVER' in os.environ and os.environ['A3_TEST_SERVER']:
    server = os.environ['A3_TEST_SERVER']
else:
    server = "http://localhost:6541"

rootpath = "/adhocracy/"

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IProposalContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + rootpath
print '  data: ' + json.dumps(data)
resp_0 = requests.post(server + rootpath, data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_0.status_code)
if resp_0.status_code == 200:
    print '  data: ' + json.dumps(resp_0.json())
    print ''

else:
    print '  data: ' + resp_0.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {
        "adhocracy.propertysheets.interfaces.IDocument": {
            "paragraphs": [],
            "title": "Der Käpt'n",
            "description": "von Peter Maria Neuhaus (titanic 9/2012)"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IProposal"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_0.json()['path']
print '  data: ' + json.dumps(data)
resp_1 = requests.post(server + resp_0.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_1.status_code)
if resp_1.status_code == 200:
    print '  data: ' + json.dumps(resp_1.json())
    print ''

else:
    print '  data: ' + resp_1.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IProposalContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + rootpath
print '  data: ' + json.dumps(data)
resp_2 = requests.post(server + rootpath, data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_2.status_code)
if resp_2.status_code == 200:
    print '  data: ' + json.dumps(resp_2.json())
    print ''

else:
    print '  data: ' + resp_2.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IProposalContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + rootpath
print '  data: ' + json.dumps(data)
resp_3 = requests.post(server + rootpath, data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_3.status_code)
if resp_3.status_code == 200:
    print '  data: ' + json.dumps(resp_3.json())
    print ''

else:
    print '  data: ' + resp_3.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_0.json()['path']
print '  data: ' + json.dumps(data)
resp_4 = requests.post(server + resp_0.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_4.status_code)
if resp_4.status_code == 200:
    print '  data: ' + json.dumps(resp_4.json())
    print ''

else:
    print '  data: ' + resp_4.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_0.json()['path']
print '  data: ' + json.dumps(data)
resp_5 = requests.post(server + resp_0.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_5.status_code)
if resp_5.status_code == 200:
    print '  data: ' + json.dumps(resp_5.json())
    print ''

else:
    print '  data: ' + resp_5.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_0.json()['path']
print '  data: ' + json.dumps(data)
resp_6 = requests.post(server + resp_0.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_6.status_code)
if resp_6.status_code == 200:
    print '  data: ' + json.dumps(resp_6.json())
    print ''

else:
    print '  data: ' + resp_6.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraphContainer"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_0.json()['path']
print '  data: ' + json.dumps(data)
resp_7 = requests.post(server + resp_0.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_7.status_code)
if resp_7.status_code == 200:
    print '  data: ' + json.dumps(resp_7.json())
    print ''

else:
    print '  data: ' + resp_7.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {},
    "content_type": "adhocracy.contents.interfaces.IParagraph"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_4.json()['path']
print '  data: ' + json.dumps(data)
resp_8 = requests.post(server + resp_4.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_8.status_code)
if resp_8.status_code == 200:
    print '  data: ' + json.dumps(resp_8.json())
    print ''

else:
    print '  data: ' + resp_8.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "Schwach ist sein Gang, mit kurzen Trippelschrittchen\nvom Heck zum Kiel, seniorenhaft verdreht.\nQuecksilberfischig jedes zweite Trittchen,\nweil er auf einem Narwal-Holzbein geht.\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_5.json()['path']
print '  data: ' + json.dumps(data)
resp_10 = requests.post(server + resp_5.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_10.status_code)
if resp_10.status_code == 200:
    print '  data: ' + json.dumps(resp_10.json())
    print ''

else:
    print '  data: ' + resp_10.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "Nur einmal schiebt der Vorhang vom Pupillchen\nsich auf: Europa retten kann nur er!\nStark wie ein Wal war früher ja sein Willchen.\nDoch heute? Käpt’n Iglo bläst nicht mehr.\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_6.json()['path']
print '  data: ' + json.dumps(data)
resp_11 = requests.post(server + resp_6.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_11.status_code)
if resp_11.status_code == 200:
    print '  data: ' + json.dumps(resp_11.json())
    print ''

else:
    print '  data: ' + resp_11.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "...\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_7.json()['path']
print '  data: ' + json.dumps(data)
resp_12 = requests.post(server + resp_7.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_12.status_code)
if resp_12.status_code == 200:
    print '  data: ' + json.dumps(resp_12.json())
    print ''

else:
    print '  data: ' + resp_12.text
    print ''
    print 'giving up!'
    exit(1)

data = {
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
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_0.json()['path']
print '  data: ' + json.dumps(data)
resp_13 = requests.post(server + resp_0.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_13.status_code)
if resp_13.status_code == 200:
    print '  data: ' + json.dumps(resp_13.json())
    print ''

else:
    print '  data: ' + resp_13.text
    print ''
    print 'giving up!'
    exit(1)

data = {
    "data": {
        "adhocracy.propertysheets.interfaces.IParagraph": {
            "text": "Sein Bart ist vom Vorüberziehn der Stäbchen\nganz weiß geworden, so wie nicht mehr frisch.\nIhm ist, als wenn es tausend Stäbchen gäbchen\nund in den tausend Stäbchen keinen Fisch.\n"
        }
    },
    "content_type": "adhocracy.contents.interfaces.IParagraph"
}
print '====================================================================== [REQUEST]'
print '  method: ' + 'post'
print '  uri: ' + server + resp_4.json()['path']
print '  data: ' + json.dumps(data)
resp_19 = requests.post(server + resp_4.json()['path'], data=json.dumps(data), headers={'content-type': 'text/json',    'follows': resp_8.json()['path'],})
print ''

print '---------------------------------------------------------------------- [RESPONSE]'
print '  code: ' + str(resp_19.status_code)
if resp_19.status_code == 200:
    print '  data: ' + json.dumps(resp_19.json())
    print ''

else:
    print '  data: ' + resp_19.text
    print ''
    print 'giving up!'
    exit(1)


print 'success!'
