from pyramid.view import view_config
from adhocracy.core.models.interfaces import IContainer


class ContainerView(object):

    def __init__(self, context, request):
            self.context = context
            self.request = request

    #default view
    @view_config(context=IContainer,
                 renderer='container_templates/view.pt')
    def __call__(self):
        return {'project': 'container'}
