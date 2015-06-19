from unittest.mock import Mock
from pyramid import testing


def test_set_root_acms(monkeypatch):
    from adhocracy_core.resources.root import root_acm
    from .root import spd_acm
    from .subscriber import set_root_acms
    mock_set_acms = Mock()
    monkeypatch.setattr('adhocracy_spd.resources.subscriber'
                        '.set_acms_for_app_root', mock_set_acms)
    event = Mock()
    set_root_acms(event)
    mock_set_acms.assert_called_with(event.app, (spd_acm, root_acm))


