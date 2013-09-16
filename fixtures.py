#!/usr/bin/python

import requests
import json
from pprint import pprint
import random


verbose = False

root_url = 'http://localhost:6541'
prop_name = 'no_more_mosquitos'


def run(request, path, *params):
    """
    Executes a request and prints debugging info to stdout if verbose == True.
    """
    response = request(root_url + path, *params)
    if verbose:
        pprint((request.__name__, params))
        pprint(response)
        if (response.ok):
            pprint(response.json())
    if response.status_code != 200:
        print(path)
        raise Exception("status_code == " + str(response.status_code))
    return response


def mk_new_proposal():
    # FIXME: server should correctly handle clashing proposal names
    id = random.randint(0, 100000000000000000000)
    data = {
        'content_type': 'adhocracy.interfaces.IProposalContainer',
        'data': {'adhocracy.interfaces.IName': {'name': "Proposal_" + str(id)}}
    }

    response = run(requests.post, '/adhocracy', json.dumps(data))
    dag_path = response.json()['path']

    response = run(requests.get, dag_path + "/_versions")
    first_version_path = response.json()['children'][0]['path']
    return (dag_path, first_version_path)

def mk_new_paragraph():
    # FIXME: server should correctly handle clashing proposal names
    id = random.randint(0, 100000000000000000000)
    data = {
        'content_type': 'adhocracy.interfaces.IParagraphContainer',
        'data': {
            'adhocracy.interfaces.IName': {'name': "Paragraph_" + str(id)}
        }
    }

    response = run(requests.post, '/adhocracy', json.dumps(data))
    dag_path = response.json()['path']

    response = run(requests.get, dag_path + "/_versions")
    first_version_path = response.json()['children'][0]['path']

    return (dag_path, first_version_path)

def put_new(path, function):
    """
    PUTs a new version of an object identified by a path through a given
    function. Sets also the follows field.
    Returns the new path.
    """
    object = run(requests.get, path).json()
    oid = object['meta']['oid']
    new = function(object)
    new['data']['adhocracy.interfaces.IVersionable']['follows'] = [oid]
    response = run(requests.put, path, json.dumps(new))
    return response.json()['path']

def get(path):
    """
    Retrieves an object with method GET and returns its value as a python object.
    """
    return run(requests.get, path).json()

def buildFixtures():
    (proposal, proposal1) = mk_new_proposal()
    (paragraphA, paragraphA1) = mk_new_paragraph()
    (paragraphB, paragraphB1) = mk_new_paragraph()

    def insert_text(text):
        def inner(paragraph):
            paragraph['data']['adhocracy.interfaces.IText']['text'] = text
            return paragraph
        return inner

    paragraphA2 = put_new(paragraphA1, insert_text("First Paragraph"))
    paragraphB2 = put_new(paragraphB1, insert_text("Second Paragraph"))

    def insert_paragraphs(proposal):
        pa_oid = get(paragraphA2)['meta']['oid']
        pb_oid = get(paragraphB2)['meta']['oid']
        proposal['data']['adhocracy.interfaces.IDocument']['paragraphs'] = \
            [pa_oid, pb_oid]
        return proposal

    proposal2 = put_new(proposal1, insert_paragraphs)

    print("created a new proposal:")
    print(root_url + proposal2)
    print(root_url + "/frontend_static/frontend.html#" + proposal2)


buildFixtures()
