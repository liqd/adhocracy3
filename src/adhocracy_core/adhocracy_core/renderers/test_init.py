from pytest import mark
from pytest import fixture
from pytest import raises


@fixture
def integration(config):
    config.include('adhocracy_core.renderers')
    return config


class TestYAMLToPython:

    @mark.usefixtures('integration')
    def test_renderer_yaml_file(self):
        from pyramid.renderers import render
        result = render('adhocracy_core.renderers:test.yaml', {})
        assert result == {'key': 'value'}

    @mark.usefixtures('integration')
    def test_raise_if_yaml_file_does_not_exists(self):
        from pyramid.renderers import render
        with raises(ValueError):
            render('adhocracy_core.renderers:wrong.yaml', {})
