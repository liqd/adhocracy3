from pyramid.view import view_config
from pyramid.response import Response
from adhocracy.core.models import AdhocracyRoot


def testview(request):
    return {'project':'adhocracy.core'}


class AdhocracyView(object):

    def __init__(self, context, request):
            self.context = context
            self.request = request

    #default view
    @view_config(context=AdhocracyRoot,
                 renderer='adhocracycore:templates/mytemplate.pt')
    def __call__(self):
        # return template variables or html
        return {'project':'adhocracy.core'}
        #return Response('OK')

    #different view with name
    @view_config(context=AdhocracyRoot,
                 name="secondview",
                 renderer='adhocracycore:templates/mytemplate.pt')
    def secondview(self):
        return Response('OK')

