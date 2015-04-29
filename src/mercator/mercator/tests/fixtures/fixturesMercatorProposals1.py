# -*- encoding: utf-8 -*-
# you can execute this module from $A3_ROOT with ./bin/ipython as interpreter.

import os
import json
import requests
from random import choice
from random import randint

from adhocracy_frontend.tests.acceptance.shared import get_random_string

root_uri = 'http://localhost:9080'
verbose = False

# for more javascript-ish json representation:
null = None
true = True
false = False

def login():
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
    return response.json()


create_proposal_batch = \
    [{"method": "POST", "path": "http://localhost/mercator", "body": {
        "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposal",
        "data": {"adhocracy_core.sheets.name.IName": {"name": "proposal2"}},
        "first_version_path": "@pn2", "root_versions": [],
        "parent": "http://localhost/mercator"}, "result_path": "@pn1",
      "result_first_version_path": "@pn2"}, {"method": "POST", "path": "@pn1",
                                             "body": {
                                                 "content_type":
                                                     "adhocracy_mercator.resources.mercator.IExperience",
                                                 "data": {
                                                     "adhocracy_core.sheets.name.IName": {
                                                         "name": "experience"}},
                                                 "first_version_path": "@pn35",
                                                 "root_versions": [],
                                                 "parent": "@pn1"},
                                             "result_path": "@pn34",
                                             "result_first_version_path":
                                                 "@pn35"},
     {"method": "POST", "path": "@pn34", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IExperienceVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn35"]},
             "adhocracy_mercator.sheets.mercator.IExperience": {
                 "experience": "experience"}}, "root_versions": [], "parent": "@pn34"},
      "result_path": "@pn36", "result_first_version_path": "@pn37"},
     {"method": "POST", "path": "@pn1",
      "body": {"content_type": "adhocracy_mercator.resources.mercator.IFinance",
               "data": {
                   "adhocracy_core.sheets.name.IName": {"name": "finance"}},
               "first_version_path": "@pn32", "root_versions": [],
               "parent": "@pn1"}, "result_path": "@pn31",
      "result_first_version_path": "@pn32"}, {"method": "POST", "path": "@pn31",
                                              "body": {
                                                  "content_type":
                                                      "adhocracy_mercator.resources.mercator.IFinanceVersion",
                                                  "data": {
                                                      "adhocracy_core.sheets.versions.IVersionable": {
                                                          "follows": ["@pn32"]},
                                                      "adhocracy_mercator.sheets.mercator.IFinance": {
                                                          "budget": 1000,
                                                          "requested_funding": 1000,
                                                          "granted": true}},
                                                  "root_versions": [],
                                                  "parent": "@pn31"},
                                              "result_path": "@pn33",
                                              "result_first_version_path":
                                                  "@pn38"},
     {"method": "POST", "path": "@pn1", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IPartners",
         "data": {"adhocracy_core.sheets.name.IName": {"name": "partners"}},
         "first_version_path": "@pn29", "root_versions": [], "parent": "@pn1"},
      "result_path": "@pn28", "result_first_version_path": "@pn29"},
     {"method": "POST", "path": "@pn28", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IPartnersVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn29"]},
             "adhocracy_mercator.sheets.mercator.IPartners": {"partners": "partners"}},
         "root_versions": [], "parent": "@pn28"}, "result_path": "@pn30",
      "result_first_version_path": "@pn39"}, {"method": "POST", "path": "@pn1",
                                              "body": {
                                                  "content_type":
                                                      "adhocracy_mercator.resources.mercator.IValue",
                                                  "data": {
                                                      "adhocracy_core.sheets.name.IName": {
                                                          "name": "value"}},
                                                  "first_version_path": "@pn26",
                                                  "root_versions": [],
                                                  "parent": "@pn1"},
                                              "result_path": "@pn25",
                                              "result_first_version_path":
                                                  "@pn26"},
     {"method": "POST", "path": "@pn25", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IValueVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn26"]},
             "adhocracy_mercator.sheets.mercator.IValue": {"value": "relevance"}},
         "root_versions": [], "parent": "@pn25"}, "result_path": "@pn27",
      "result_first_version_path": "@pn40"}, {"method": "POST", "path": "@pn1",
                                              "body": {
                                                  "content_type":
                                                      "adhocracy_mercator.resources.mercator.ISteps",
                                                  "data": {
                                                      "adhocracy_core.sheets.name.IName": {
                                                          "name": "steps"}},
                                                  "first_version_path": "@pn23",
                                                  "root_versions": [],
                                                  "parent": "@pn1"},
                                              "result_path": "@pn22",
                                              "result_first_version_path":
                                                  "@pn23"},
     {"method": "POST", "path": "@pn22", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IStepsVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn23"]},
             "adhocracy_mercator.sheets.mercator.ISteps": {"steps": "plan"}},
         "root_versions": [], "parent": "@pn22"}, "result_path": "@pn24",
      "result_first_version_path": "@pn41"}, {"method": "POST", "path": "@pn1",
                                              "body": {
                                                  "content_type":
                                                      "adhocracy_mercator.resources.mercator.IOutcome",
                                                  "data": {
                                                      "adhocracy_core.sheets.name.IName": {
                                                          "name": "outcome"}},
                                                  "first_version_path": "@pn20",
                                                  "root_versions": [],
                                                  "parent": "@pn1"},
                                              "result_path": "@pn19",
                                              "result_first_version_path":
                                                  "@pn20"},
     {"method": "POST", "path": "@pn19", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IOutcomeVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn20"]},
             "adhocracy_mercator.sheets.mercator.IOutcome": {"outcome": "success"}},
         "root_versions": [], "parent": "@pn19"}, "result_path": "@pn21",
      "result_first_version_path": "@pn42"}, {"method": "POST", "path": "@pn1",
                                              "body": {
                                                  "content_type":
                                                      "adhocracy_mercator.resources.mercator.IStory",
                                                  "data": {
                                                      "adhocracy_core.sheets.name.IName": {
                                                          "name": "story"}},
                                                  "first_version_path": "@pn17",
                                                  "root_versions": [],
                                                  "parent": "@pn1"},
                                              "result_path": "@pn16",
                                              "result_first_version_path":
                                                  "@pn17"},
     {"method": "POST", "path": "@pn16", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IStoryVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn17"]},
             "adhocracy_mercator.sheets.mercator.IStory": {"story": "story"}},
         "root_versions": [], "parent": "@pn16"}, "result_path": "@pn18",
      "result_first_version_path": "@pn43"}, {"method": "POST", "path": "@pn1",
                                              "body": {
                                                  "content_type": "adhocracy_mercator.resources.mercator.ILocation",
                                                  "data": {
                                                      "adhocracy_core.sheets.name.IName": {
                                                          "name": "location"}},
                                                  "first_version_path": "@pn14",
                                                  "root_versions": [],
                                                  "parent": "@pn1"},
                                              "result_path": "@pn13",
                                              "result_first_version_path": "@pn14"},
     {"method": "POST", "path": "@pn13", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.ILocationVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn14"]},
             "adhocracy_mercator.sheets.mercator.ILocation": {
                 "location_is_specific": true, "location_specific_1": "Bonn",
                 "location_is_linked_to_ruhr": true}}, "root_versions": [],
         "parent": "@pn13"}, "result_path": "@pn15",
      "result_first_version_path": "@pn44"}, {"method": "POST", "path": "@pn1",
                                              "body": {
                                                  "content_type": "adhocracy_mercator.resources.mercator.IDescription",
                                                  "data": {
                                                      "adhocracy_core.sheets.name.IName": {
                                                          "name": "description"}},
                                                  "first_version_path": "@pn11",
                                                  "root_versions": [],
                                                  "parent": "@pn1"},
                                              "result_path": "@pn10",
                                              "result_first_version_path": "@pn11"},
     {"method": "POST", "path": "@pn10", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IDescriptionVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn11"]},
             "adhocracy_mercator.sheets.mercator.IDescription": {
                 "description": "prodescription"}}, "root_versions": [], "parent": "@pn10"},
      "result_path": "@pn12", "result_first_version_path": "@pn45"},
     {"method": "POST", "path": "@pn1", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IIntroduction",
         "data": {"adhocracy_core.sheets.name.IName": {"name": "introduction"}},
         "first_version_path": "@pn8", "root_versions": [], "parent": "@pn1"},
      "result_path": "@pn7", "result_first_version_path": "@pn8"},
     {"method": "POST", "path": "@pn1",
      "body": {
          "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfo",
          "data": {
              "adhocracy_core.sheets.name.IName": {
                  "name": "organization_info"}},
          "first_version_path": "@pn5",
          "root_versions": [],
          "parent": "@pn1"},
      "result_path": "@pn4",
      "result_first_version_path": "@pn5"},
     {"method": "POST", "path": "@pn4", "body": {
         "content_type": "adhocracy_mercator.resources.mercator.IOrganizationInfoVersion",
         "data": {
             "adhocracy_core.sheets.versions.IVersionable": {"follows": ["@pn5"]},
             "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                 "name": "organization name", "country": "CL",
                 "status": "registered_nonprofit", "website": "http://example.org"}},
         "root_versions": [], "parent": "@pn4"}, "result_path": "@pn6",
      "result_first_version_path": "@pn47"},
     {"method": "POST", "path": "@pn1",
      "body": {
          "content_type": "adhocracy_mercator.resources.mercator.IMercatorProposalVersion",
          "data": {
              "adhocracy_core.sheets.versions.IVersionable": {
                  "follows": ["@pn2"]},
              "adhocracy_mercator.sheets.mercator.IUserInfo": {
                  "personal_name": "pita",
                  "family_name": "pasta",
                  "country": "AR"},
              "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                  "heard_from_colleague": true,
                  "heard_elsewhere": ""},
              "adhocracy_mercator.sheets.mercator.IMercatorSubResources": {
                  "organization_info": "@pn6",
                  "description": "@pn12",
                  "location": "@pn15",
                  "story": "@pn18",
                  "outcome": "@pn21",
                  "steps": "@pn24",
                  "value": "@pn27",
                  "partners": "@pn30",
                  "finance": "@pn33",
                  "experience": "@pn36"}},
          "root_versions": [],
          "parent": "@pn1"},
      "result_path": "@pn3",
      "result_first_version_path": "@pn48"}]

update_proposal_batch = \
    [{"method": "POST",
      "path": "http://localhost/mercator/proposal2/organization_info/", "body": {
        "content_type": "adhocracy_mercator.resources.mercator"
                        ".IOrganizationInfoVersion",
        "data": {"adhocracy_core.sheets.versions.IVersionable": {"follows": [
            "http://localhost/mercator/proposal2/organization_info"
            "/VERSION_0000001/"]},
                 "adhocracy_core.sheets.metadata.IMetadata": {"deleted": false,
                                                              "preliminaryNames":
                                                                  {"state": 77}},
                 "adhocracy_mercator.sheets.mercator.IOrganizationInfo": {
                     "name": "organization name Updated", "country": "CL",
                     "status": "registered_nonprofit",
                     "website": "http://example.org"}}, "root_versions": [],
        "parent": "http://localhost/mercator/proposal2/organization_info/"},
      "result_path": "@pn65", "result_first_version_path": "@pn77"},
     {"method": "POST", "path": "http://localhost/mercator/proposal2/", "body": {
         "content_type": "adhocracy_mercator.resources.mercator"
                         ".IMercatorProposalVersion",
         "data": {
             "adhocracy_core.sheets.metadata.IMetadata": {"deleted": false,
                                                          "preliminaryNames":
                                                              {"state": 78}},
             "adhocracy_core.sheets.versions.IVersionable": {"follows": [
                 "http://localhost/mercator/proposal2/VERSION_0000001/"]},
             "adhocracy_mercator.sheets.mercator.IUserInfo": {
                 "personal_name": "pita Updated", "family_name": "pasta",
                 "country": "AR"}}, "root_versions": [],
         "parent": "http://localhost/mercator/proposal2/"}, "result_path": "@pn64",
      "result_first_version_path": "@pn78"}]


def _create_proposal():
    name = get_random_string()

    location_is_specific = true if randint(0,1) else false
    location_is_linked_to_ruhr = true if randint(0,1) else false
    location_is_online = true if randint(0,1) else false
    location_specific_1 = None

    if not (location_is_specific or
            location_is_linked_to_ruhr or
            location_is_online):
        location_is_online = true
    if  location_is_specific:
        location_specific_1 = "location_is_specific"

    return   [{
                "path": "" + root_uri + "/mercator/",
                "body": {
                    "parent": "" + root_uri + "/mercator/",
                    "data": {
                        "adhocracy_core.sheets.name.IName": {
                            "name": name
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
                            "name": "experience"
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
                            "name": "finance"
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
                            "budget": randint(0,50000),
                            "other_sources": "hidden treasure",
                            "requested_funding": randint(0,50000)
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
                            "name": "partners"
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
                            "name": "steps"
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
                            "name": "outcome"
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
                            "name": "story"
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
                            "name": "description"
                        }
                    },
                    "root_versions": [],
                    "content_type": "adhocracy_mercator.resources.mercator.IDescription",
                    "first_version_path": "@pn8a"
                },
                "result_path": "@pn7a",
                "method": "POST",
                "result_first_version_path": "@pn8a"
            },
            {
                "path": "@pn7a",
                "body": {
                    "parent": "@pn7a",
                    "data": {
                        "adhocracy_core.sheets.versions.IVersionable": {
                            "follows": [
                                "@pn8a"
                            ]
                        },
                        "adhocracy_mercator.sheets.mercator.IDescription": {
                            "description": "description"
                        }
                    },
                    "root_versions": [],
                    "content_type": "adhocracy_mercator.resources.mercator.IDescriptionVersion"
                },
                "result_path": "@pn9a",
                "method": "POST",
                "result_first_version_path": "@pn41a"
            },
            {
                "path": "@pn31",
                "body": {
                    "parent": "@pn31",
                    "data": {
                        "adhocracy_core.sheets.name.IName": {
                            "name": "location"
                        }
                    },
                    "root_versions": [],
                    "content_type": "adhocracy_mercator.resources.mercator.ILocation",
                    "first_version_path": "@pn8b"
                },
                "result_path": "@pn7b",
                "method": "POST",
                "result_first_version_path": "@pn8b"
            },
            {
                "path": "@pn7b",
                "body": {
                    "parent": "@pn7b",
                    "data": {
                        "adhocracy_core.sheets.versions.IVersionable": {
                            "follows": [
                                "@pn8b"
                            ]
                        },
                        "adhocracy_mercator.sheets.mercator.ILocation": {
                            "location_specific_1": location_specific_1,
                            "location_is_specific": location_is_specific,
                            "location_is_online": location_is_online,
                            "location_is_linked_to_ruhr": location_is_linked_to_ruhr,
                        }
                    },
                    "root_versions": [],
                    "content_type": "adhocracy_mercator.resources.mercator.ILocationVersion"
                },
                "result_path": "@pn9b",
                "method": "POST",
                "result_first_version_path": "@pn41b"
            },
            {
                "path": "@pn31",
                "body": {
                    "parent": "@pn31",
                    "data": {
                        "adhocracy_core.sheets.name.IName": {
                            "name": "introduction"
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
                            "teaser": get_random_string(300, whitespace=True),
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
                            "name": "organizationinfo"
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
                            "planned_date": "2014-11-19T13:19:25.405Z",
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
                        "adhocracy_core.sheets.title.ITitle": {
                            "title": name
                        },
                        "adhocracy_mercator.sheets.mercator.IHeardFrom": {
                            "heard_from_colleague": true,
                            "heard_elsewhere": "i'm not telling"
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
                            "description": "@pn9a",
                            "location": "@pn9b",
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
            }]

def create_proposals(user_path="", user_token="", n=5, expect_error=False):
    proposals = []

    uri = root_uri + "/batch"
    def headers(length):
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip,deflate",
            "Connection": "keep-alive",
            "X-User-Token": user_token,
            "X-User-Path": user_path,
            "Accept-Language": "en-US,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
            "Content-Length": length
        }

    for i in range(n):
        requested_proposal = _create_proposal()

        body = json.dumps(requested_proposal)
        response = requests.post(uri, headers=headers(str(len(body))), data=body)
        if verbose:
            print('\n')
            print(uri)
            print(headers(str(len(body))))
            print(body)
            print(response)
            print(response.text)
        if not expect_error:
            assert response.status_code == 200

        proposals.append(requested_proposal)

    return proposals


if __name__ == "__main__":
    credentials = login()
    create_proposals(credentials['user_path'], credentials['user_token'])
