"""Rest API view for batch API."""
from logging import getLogger

from pyramid.view import view_config
from pyramid.view import view_defaults

from adhocracy.resources.root import IRootPool
from adhocracy.rest.schemas import POSTBatchRequestSchema
from adhocracy.rest.views import RESTView

logger = getLogger(__name__)


@view_defaults(
    renderer='simplejson',
    context=IRootPool,
)
class BatchView(RESTView):

    """Process batch requests."""

    validation_POST = (POSTBatchRequestSchema, [])

    @view_config(name='batch',
                 request_method='POST',
                 content_type='application/json')
    def post(self) -> dict:
        """Create new resource and get response data."""
        # TODO implement
        items = self.request.validated['items']
        return {'itemcount': len(items)}


def includeme(config):  # pragma: no cover
    """Register batch view."""
    config.scan('.batchview')
