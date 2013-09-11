"""Helper to run tests"""


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


