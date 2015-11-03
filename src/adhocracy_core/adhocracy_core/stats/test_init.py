from py.test import mark


@mark.usefixtures('integration')
def test_add_statsd_client_to_registry_if_runtim_statitics_enabled(config):
    from statsd.client import StatsClient
    config.registry.settings['substanced.statsd.enabled'] = True
    config.include('adhocracy_core.stats')
    client = config.registry['statsd_client']
    assert isinstance(client, StatsClient)
