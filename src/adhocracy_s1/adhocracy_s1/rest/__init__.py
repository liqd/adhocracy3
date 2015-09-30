"""Rest API customizations."""
from datetime import datetime
from adhocracy_core.rest.schemas import INDEX_EXAMPLE_VALUES


def includeme(config):
    """Add example value for index `descision_date`."""
    INDEX_EXAMPLE_VALUES['decision_date'] = datetime.now()
