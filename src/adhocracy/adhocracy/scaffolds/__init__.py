"""Create scaffolds to customize or extend adhocracy."""
from pyramid.scaffolds import PyramidTemplate
import random
import string


class AdhocracyExtensionTemplate(PyramidTemplate):

    """Basic python egg that extends adhocracy."""

    def pre(self, command, output_dir, vars):  # pragma: no cover
        size = 10
        chars = string.ascii_letters + string.digits
        vars['random_password'] = ''.join(
            random.choice(chars) for x in range(size)
        )
        return PyramidTemplate.pre(self, command, output_dir, vars)
    _template_dir = 'adhocracy'
    summary = 'Adocracy extension app'
