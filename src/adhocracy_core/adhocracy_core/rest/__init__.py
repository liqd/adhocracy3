"""Configure rest api packages."""
from pyramid.view import view_config
from adhocracy_core.authentication import validate_user_headers
from adhocracy_core.authentication import validate_anonymize_header
from adhocracy_core.authentication import validate_password_header
from adhocracy_core.caching import set_cache_header
from adhocracy_core.rest.schemas import validate_request_data
from adhocracy_core.rest.schemas import validate_visibility


class api_view(view_config):  # noqa
    """ A function\class\method decorator to configure a rest api :term:`view`.

    It works like the normal :class:`pyramid.view.view_config` decorator exept
    the following defaults are set::

        renderer='json'
        decorator = [validate_user_headers,
                     validate_anonymize_header,
                     validate_visibility,
                     set_cache_header]

    In addition it is possible to set a :term:`Schema` to validate the request
    body or querystring::

        schema=myschema

    If set the `validate_request_data` decorator is initialized with it and
    added to the decorator settings.

    Example::

        @api_view(context=IMyContentType,
                  schema=MySchema,
                  request_method=POST,
                  )
        def post_rest_view(context:IResource, request: IRequest) -> dict:
            appstruct = request.validated
            ...
    """

    def __call__(self, wrapped):

        def add_view(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_view(view=ob, **settings)

        info = self._attach_to_config(wrapped, add_view)
        settings = self._create_view_settings(wrapped, info)

        return wrapped

    def _attach_to_config(self, wrapped, add_view):
        info = self.venusian.attach(wrapped,
                                    add_view,
                                    category='adhocracy',
                                    depth=2)
        return info

    def _create_view_settings(self, wrapped, info) -> dict:
        settings = {'renderer': 'json',
                    'decorator': [validate_user_headers,
                                  validate_anonymize_header,
                                  validate_password_header,
                                  validate_visibility,
                                  set_cache_header,
                                  ]
                    }
        settings.update(self.__dict__)
        if 'schema' in settings:
            validate_data = validate_request_data(settings['schema'])
            settings['decorator'].append(validate_data)
            del settings['schema']
        if 'attr' not in settings and info.scope == 'class':
            settings['attr'] = wrapped.__name__  # work with methods/functions
        return settings


def includeme(config):  # pragma: no cover
    """Include all rest views configuration."""
    config.include('.views')
    config.include('.batchview')
    config.add_request_method(lambda x: [], name='errors', reify=True)
    config.add_request_method(lambda x: {}, name='validated', reify=True)
    config.include('.exceptions')
    config.include('.subscriber')
