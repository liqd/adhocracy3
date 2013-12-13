"""functional testing helpers"""


def settings_functional():
    """Return minimal pyramid config for functional tests."""
    settings = {}
    settings.update({"pyramid.includes": ["pyramid_zodbconn", "pyramid_tm"],
                     "substanced.initial_login": "admin",
                     "substanced.initial_password": "admin",
                     "substanced.initial_email": "admin@example.com",
                     "substanced.secret": "secret",
                     "substanced.autosync_catalogs": "true",
                     "substanced.statsd.enabled": "false ",
                     "substanced.autoevolve": "true",
                     "zodbconn.uri": "memory://",
                     })
    return settings
