from pyramid.renderers import JSON
from pyramid.renderers import _marker
from colander import _null


def colander_null_json_adapter(context, request):
    serializable = _marker
    if isinstance(context, _null):
        serializable = None
    return serializable


jsoncolander = JSON(adapters=[(_null, colander_null_json_adapter)], indent=2)


def includeme(config):  # pragma: no cover

    config.include("cornice")
    config.scan(".views")
    config.scan(".exceptions")
    ##config#.add_renderer('jsoncolander', jsoncolander)
    #config.include(".views")
