#!/usr/bin/python

import requests
import json
from pprint import pprint


root_url = 'http://localhost:6541'
prop_name = 'no_more_mosquitos'


def run(request, *params):
    verbose = True

    response = request(*params)
    if verbose:
        pprint((request.__name__, params))
        pprint(response)
        if (response.ok):
            pprint(response.json())
    return response


# produces internal error on clean zodb state (git version
# ffcf498c9820ef22ce7b8c3399330157e17459a8).  (there is probably an
# error in this script, but it should not make the server crash,
# right?)
def utest1():
    data = {'content_type': 'adhocracy.interfaces.IProposalContainer',
            'data': {'adhocracy.interfaces.IName': {'name': prop_name}}}
    r = run(requests.post, root_url + '/adhocracy', json.dumps(data))

    r = run(requests.get, root_url + '/adhocracy/' + prop_name + '/_versions')
    children = r.json()["children"]

    url = children[0]['path']

    r = run(requests.get, root_url + url)

    obj = r.json()["data"]
    meta = r.json()["meta"]

    obj['adhocracy.interfaces.IDocument']['title'] = 'No More Mosquitos!'
    obj['adhocracy.interfaces.IVersionable'] = {'follows': [url]}

    r = run(requests.put, root_url + url, json.dumps({ 'content_type': 'adhocracy.interfaces.IProposal', 'data': obj }))

    # ...  now do the same thing once more.
    data = {'content_type': 'adhocracy.interfaces.IProposalContainer',
            'data': {'adhocracy.interfaces.IName': {'name': prop_name}}}
    r = run(requests.post, root_url + '/adhocracy', json.dumps(data))      # i think this should yield a clean error response from backend.  -mf

    r = run(requests.get, root_url + '/adhocracy/' + prop_name + '/_versions')
    children = r.json()["children"]

    url = children[0]['path']

    r = run(requests.get, root_url + url)

    obj = r.json()["data"]
    meta = r.json()["meta"]

    obj['adhocracy.interfaces.IDocument']['title'] = 'No More Mosquitos!'
    obj['adhocracy.interfaces.IVersionable'] = {'follows': [url]}

    r = run(requests.put, root_url + url, json.dumps({ 'content_type': 'adhocracy.interfaces.IProposal', 'data': obj }))


def buildFixtures():
    data = {'content_type': 'adhocracy.interfaces.IProposalContainer',
            'data': {'adhocracy.interfaces.IName': {'name': prop_name}}}
    r = run(requests.post, root_url + '/adhocracy', json.dumps(data))

    r = run(requests.get, root_url + '/adhocracy/' + prop_name + '/_versions')
    children = r.json()["children"]
    #pprint(children)

    url = children[0]['path']
    #pprint(url)

    r = run(requests.get, root_url + url)

    obj = r.json()["data"]
    meta = r.json()["meta"]

    obj['adhocracy.interfaces.IDocument']['title'] = 'No More Mosquitos!'
    obj['adhocracy.interfaces.IVersionable'] = {'follows': [url]}

    pprint(obj)

    r = run(requests.put, root_url + url, json.dumps({ 'content_type': 'adhocracy.interfaces.IProposal', 'data': obj }))
    url = r.json()['path']

    obj['adhocracy.interfaces.IDocument']['paragraphs'] = ['wef', 'ofq']
    r = run(requests.put, root_url + url, json.dumps({ 'content_type': 'adhocracy.interfaces.IProposal', 'data': obj }))


#buildFixtures()
utest1()

#r = run(requests.options, root_url + '/adhocracy');
#r = run(requests.get, root_url + '/adhocracy');
#r = run(requests.get, u'http://localhost:6541/adhocracy/no_more_mosquitos/_versions/B2BVZ11')


