# -*- encoding: utf-8 -*-
# [call this script from a3 root with ./bin/python3.4 as interpreter.]
# FIXME: Doesn't work as requests is missing. Use a Python with requests
# installed.

import os
import json
import requests
from random import choice
from random import randint

# FIXME: root_uri must be constructed from etc/*.ini, not hard-coded here!
root_uri = 'http://localhost:6542'
verbose = True

ALPHABET = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
def get_random_string(n=10):
    return "".join(choice(ALPHABET) for i in range(n));

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


def create_proposals(n=5):
    proposals = []

    #login()

    uri = root_uri + "/batch"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip,deflate",
        "Connection": "keep-alive",
        "X-User-Path": "" + root_uri + "/principals/users/0000000/",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
        "Content-Length": "8206"
    }

    for i in range(n):
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

        requested_proposal = [
            {
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
                            "location_specific_1": location_specific_1,
                            "location_is_specific": location_is_specific,
                            "location_is_online": location_is_online,
                            "location_is_linked_to_ruhr": location_is_linked_to_ruhr,
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
                            "title": name
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
        ]

        body = json.dumps(requested_proposal)
        response = requests.post(uri, headers=headers, data=body)
        if verbose:
            print('\n')
            print(uri)
            print(headers)
            print(body)
            print(response)
            print(response.text)
        assert response.status_code == 200

        proposals.append(requested_proposal)

    return proposals

if __name__ == "__main__":
    create_proposals()
