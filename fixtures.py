#!/usr/bin/python

import requests
import json
from pprint import pprint

root_url = 'http://localhost:6541/adhocracy/'


do_everything = False


if do_everything:
    # 1st prop container: no_more_mosquitos
    data = { 'content_type': 'adhocracy.interfaces.IProposalContainer',
             'data': { 'adhocracy.interfaces.IName': { 'name': 'no_more_mosquitos' } }
           }
    resp = requests.post(root_url, data=json.dumps(data))
    pprint(resp)
    pprint(resp.json())


if do_everything or True:
    resp = requests.get(root_url + '/no_more_mosquitos/_versions')
    predecessor = resp.json()['children'][0]  # just take the first one (if we really just created it, that's the only one)

    # v2.1, follows v1
    data = { 'content_type': 'adhocracy.interfaces.IProposal',
             'data': { 'adhocracy.interfaces.IProposal': { 'title': 'v2.1', 'description': 'nulleinsneunzwei' },
                       'adhocracy.interfaces.IVersionable': { 'follows': [predecessor['oid']] },
                     }
           }
    resp = requests.put(root_url + '/no_more_mosquitos/_versions/' + str(predecessor['name']), data=json.dumps(data))

    pprint(resp)
    pprint(resp.json())
    exit(0)  # this is still crashing.

    var v21 = resp.json())

    # v2.2, follows v1
    # v2.3, follows v1
    # v3.1, follows v2.3
    # v3.2, follows v2.3
    # v4.1, follows v2.2



print "all done!"
exit(0)
