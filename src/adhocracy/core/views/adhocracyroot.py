from pyramid.view import view_config
from pyramid.response import Response
from adhocracy.core.models.adhocracyroot import AdhocracyRoot


def testview(request):
    return {'project':'adhocracy.core'}


class AdhocracyRootView(object):

    def __init__(self, context, request):
            self.context = context
            self.request = request

    #default view
    @view_config(context=AdhocracyRoot,
                 renderer='adhocracyroot_templates/view.pt')
    def __call__(self):
        return {'project':'adhocracy.core'}

    #different view with name
    @view_config(context=AdhocracyRoot,
                 name="secondview",
                 renderer='adhocracyroot_templates/secondview.pt')
    def secondview(self):
        return Response('OK')

