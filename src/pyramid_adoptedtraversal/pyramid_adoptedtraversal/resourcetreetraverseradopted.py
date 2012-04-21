import warnings

from zope.interface import (
    implementer,
    Interface,
)
from pyramid.traversal import (
    ResourceTreeTraverser,
    split_path_info,
    empty,
    )
from pyramid.interfaces import (
    ITraverser,
    VH_ROOT_KEY,
    )
from pyramid.compat import (
    is_nonstr_iter,
    decode_path_info,
    )
from pyramid.exceptions import URLDecodeError
from pyramid_adoptedtraversal.interfaces import IChildsDictLike


with warnings.catch_warnings():
    warnings.filterwarnings('ignore')


@implementer(ITraverser)
class ResourceTreeTraverserAdopted(ResourceTreeTraverser):
    """ Copied from pyramid.traversal.ResourceTreeTraverser.

        Instead of calling object.__getitem__ directly
        it tries to call IChildDitcLike(object).__getitem__.
        The default adapter is just a proxy to object.__getitem__

    """

    def __call__(self, request):
        try:
            environ = request.environ
        except AttributeError:
            # In BFG 1.0 and before, this API expected an environ
            # rather than a request; some bit of code may still be
            # passing us an environ.  If so, deal.
            environ = request
            depwarn = ('Passing an environ dictionary directly to a traverser '
                       'is deprecated in Pyramid 1.1.  Pass a request object '
                       'instead.')
            warnings.warn(depwarn, DeprecationWarning, 2)

        if 'bfg.routes.matchdict' in environ:
            matchdict = environ['bfg.routes.matchdict']

            path = matchdict.get('traverse', '/') or '/'
            if is_nonstr_iter(path):
                # this is a *traverse stararg (not a {traverse})
                # routing has already decoded these elements, so we just
                # need to join them
                path = '/'.join(path) or '/'

            subpath = matchdict.get('subpath', ())
            if not is_nonstr_iter(subpath):
                # this is not a *subpath stararg (just a {subpath})
                # routing has already decoded this string, so we just need
                # to split it
                subpath = split_path_info(subpath)

        else:
            # this request did not match a route
            subpath = ()
            try:
                # empty if mounted under a path in mod_wsgi, for example
                path = decode_path_info(environ['PATH_INFO'] or '/')
            except KeyError:
                path = '/'
            except UnicodeDecodeError as e:
                raise URLDecodeError(e.encoding, e.object, e.start, e.end,
                                     e.reason)

        if VH_ROOT_KEY in environ:
            # HTTP_X_VHM_ROOT
            vroot_path = decode_path_info(environ[VH_ROOT_KEY])
            vroot_tuple = split_path_info(vroot_path)
            vpath = vroot_path + path # both will (must) be unicode or asciistr
            vroot_idx = len(vroot_tuple) -1
        else:
            vroot_tuple = ()
            vpath = path
            vroot_idx = -1

        root = self.root
        ob = vroot = root

        if vpath == '/': # invariant: vpath must not be empty
            # prevent a call to traversal_path if we know it's going
            # to return the empty tuple
            vpath_tuple = ()
        else:
            # we do dead reckoning here via tuple slicing instead of
            # pushing and popping temporary lists for speed purposes
            # and this hurts readability; apologies
            i = 0
            view_selector = self.VIEW_SELECTOR
            vpath_tuple = split_path_info(vpath)
            for segment in vpath_tuple:
                if segment[:2] == view_selector:
                    return {'context':ob,
                            'view_name':segment[2:],
                            'subpath':vpath_tuple[i+1:],
                            'traversed':vpath_tuple[:vroot_idx+i+1],
                            'virtual_root':vroot,
                            'virtual_root_path':vroot_tuple,
                            'root':root}
                try:
                    # CHANGED: try to use adaper to get the __getitem__ method
                    try:
                        getitem = IChildsDictLike(ob).__getitem__
                    except TypeError:
                        getitem = ob.__getitem__
                except AttributeError:
                    return {'context':ob,
                            'view_name':segment,
                            'subpath':vpath_tuple[i+1:],
                            'traversed':vpath_tuple[:vroot_idx+i+1],
                            'virtual_root':vroot,
                            'virtual_root_path':vroot_tuple,
                            'root':root}

                try:
                    next = getitem(segment)
                except KeyError:
                    return {'context':ob,
                            'view_name':segment,
                            'subpath':vpath_tuple[i+1:],
                            'traversed':vpath_tuple[:vroot_idx+i+1],
                            'virtual_root':vroot,
                            'virtual_root_path':vroot_tuple,
                            'root':root}
                if i == vroot_idx:
                    vroot = next
                ob = next
                i += 1

        return {'context':ob, 'view_name':empty, 'subpath':subpath,
                'traversed':vpath_tuple, 'virtual_root':vroot,
                'virtual_root_path':vroot_tuple, 'root':root}
