"""Helper to run tests"""
import copy
import json
import pprint

config = {"pyramid.includes": ["pyramid_zodbconn", "pyramid_tm"],
          "zodbconn.uri": "memory://",
          "substanced.secret": "seekri1",
          "substanced.initial_login": "admin",
          "substanced.initial_password": "admin",
          "substanced.initial_email": "admin@example.com",
          "substanced.autosync_catalogs": "true",
          "substanced.statsd.enabled": "false ",
          "substanced.autoevolve": "true",
    }


def sort_dict(d, sort_paths):
    d2 = copy.deepcopy(d)
    for path in sort_paths:
        base = reduce(lambda d, seg: d[seg], path[:-1], d2)
        base[path[-1]] = sorted(base[path[-1]])
    return d2


def pprint_json(json_dict):
    json_dict_sorted = sort_dict(json_dict)
    py_dict = json.dumps(json_dict_sorted, sort_keys=True, indent=4, separators=(',', ': '))
    pprint.pprint(py_dict)


