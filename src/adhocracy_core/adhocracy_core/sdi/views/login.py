"""Logout page."""
from pyramid.authentication import Authenticated
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.renderers import get_renderer
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.security import remember
from pyramid.security import forget
from pyramid.session import check_csrf_token
from pyramid.traversal import resource_path
from substanced.event import LoggedIn
from substanced.sdi import mgmt_view

from adhocracy_core.interfaces import IRolesUserLocator


@mgmt_view(name='login',
           renderer='substanced.sdi.views:templates/login.pt',
           tab_condition=False,
           permission=NO_PERMISSION_REQUIRED
           )
@mgmt_view(renderer='substanced.sdi.views:templates/login.pt',
           context=HTTPForbidden,
           permission=NO_PERMISSION_REQUIRED,
           tab_condition=False
           )
@mgmt_view(renderer='substanced.sdi.views:templates/forbidden.pt',
           context=HTTPForbidden,
           permission=NO_PERMISSION_REQUIRED,
           effective_principals=Authenticated,
           tab_condition=False
           )
def login(context, request):
    """Login form."""
    login_url = request.sdiapi.mgmt_path(request.context, 'login')
    referrer = request.url
    if '/auditstream-sse' in referrer:
        return HTTPForbidden()
    if login_url in referrer:
        referrer = request.sdiapi.mgmt_path(request.virtual_root)
    came_from = request.session.setdefault('sdi.came_from', referrer)
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        try:
            check_csrf_token(request)
        except:
            request.sdiapi.flash('Failed login (CSRF)', 'danger')
        else:
            login = request.params['login']
            password = request.params['password']
            adapter = request.registry.queryMultiAdapter((context, request),
                                                         IRolesUserLocator)
            user = adapter.get_user_by_login(login)
            if user is not None:
                request.session.pop('sdi.came_from', None)
                headers = remember(request, resource_path(user))
                msg = LoggedIn(login, user, context, request)
                request.registry.notify(msg)
                return HTTPFound(location=came_from,
                                 headers=headers)
            request.sdiapi.flash('Failed login', 'danger')

    # Pass this through FBO views (e.g., forbidden) which use its macros.
    template = get_renderer('substanced.sdi.views:templates/login.pt')\
        .implementation()
    return dict(url=request.sdiapi.mgmt_path(request.virtual_root, '@@login'),
                came_from=came_from,
                login=login,
                password=password,
                login_template=template,
                )


@mgmt_view(name='logout',
           tab_condition=False,
           permission=NO_PERMISSION_REQUIRED
           )
def logout(request):
    """Logout user (remove authentication cookies)."""
    headers = forget(request)
    location = request.sdiapi.mgmt_path(request.context)
    return HTTPFound(location=location, headers=headers)
