"""Autogenerate forms based on :term:`schema`."""
from substanced.form import FormView as SDFormView
from substanced.schema import Schema as CSRFSchema

from deform import Form


class FormView(SDFormView):
    """View class that autogenerates forms based on :term:`schema` .

    Uses :mod:`colander` schema to define the data structure and
    validators and :mod:`deform` to render html forms.
    """

    def _build_form(self) -> tuple:
        """Build html form for :term:`schema`.

        Changed behavior:

        - expected self.schema to have all needed bindings

        - add CSRF protection to self.schema

        - make deform widgets work with readonly schema fields
        """
        self._add_csrf_token_to_schema()
        config = {'use_ajax': getattr(self, 'use_ajax', False),
                  'ajax_options ': getattr(self, 'ajax_options', '{}'),
                  'action': getattr(self, 'action', ''),
                  'method': getattr(self, 'method', 'POST'),
                  'formid': getattr(self, 'formid', 'deform'),
                  'autocomplete': getattr(self, 'autocomplete', None),
                  'buttons': self.buttons,
                  }
        form = self.form_class(self.schema, **config)
        self.before(form)
        self._setup_readonly_widgets(form)
        resources = form.get_widget_resources()
        return (form, resources)

    def _add_csrf_token_to_schema(self):
        csrf_schema = CSRFSchema()
        for child in self.schema:
            csrf_schema.add(child)
        csrf_schema.validator = self.schema.validator
        bindings = self.schema.bindings
        bindings['_csrf_token_'] = self.request.session.get_csrf_token()
        self.schema = csrf_schema.bind(**bindings)

    def _setup_readonly_widgets(self, form: Form):
        """Set readonly template for widgets if schema field is readonly."""
        is_readonly = getattr(form.schema, 'readonly', False)
        if is_readonly:
            form.widget.readonly = True  # set readonly template
        for subfield in getattr(form, 'children', []):
            self._setup_readonly_widgets(subfield)
