from django.views.generic import (
    TemplateView, FormView,
)

from .forms import BaseCSVImportForm
from django.shortcuts import redirect
from io import TextIOWrapper


class BaseImportView(FormView):
    """
    importer_class

    """
    form_class = BaseCSVImportForm
    template_context = {}
    #template_name = 'ui/base_import.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BaseImportView, self).get_context_data(*args, **kwargs)
        context.update(self.template_context)
        return context

    def get_fixed_values(self, valid_form):
        return {}

    def get_session_prefix(self):
        key = "%s" % self.importer_class.__class__.__name__
        return key

    def get_session_var(self, varname):
        return "%s_%s" % (self.get_session_prefix(), varname)

    def form_valid(self, form):
        importer = self.importer_class()
        csv_file = form.cleaned_data.get('csv_file')
        stream = TextIOWrapper(csv_file.file, encoding=self.request.encoding)
        rows = importer.get_rows_from_stream(stream)
        self.request.session[self.get_session_var('rows')] = rows
        self.request.session[self.get_session_var('fixed_values')] = self.get_fixed_values(form)

        return super(BaseImportView, self).form_valid(form)


class BaseImportProcessView(TemplateView):
    """
    importer_class
    import_url
    """
    template_context = {}
    #template_name = 'ui/base_import_process.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BaseImportProcessView, self).get_context_data(*args, **kwargs)
        context.update(self.template_context)
        context['import_url'] = self.import_url
        return context

    def get_session_prefix(self):
        key = "%s" % self.importer_class.__class__.__name__
        return key

    def get_session_var(self, varname):
        return "%s_%s" % (self.get_session_prefix(), varname)

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get(self.get_session_var('rows')):
            return redirect(self.import_url)
        return super(BaseImportProcessView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        rows = request.session.get(self.get_session_var('rows'))
        fixed_values = request.session.get(self.get_session_var('fixed_values'))

        importer = self.importer_class()
        results = importer.import_rows(rows, fixed_values=fixed_values, commit=False)
        context = self.get_context_data()
        context["results"] = results
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        rows = request.session.get(self.get_session_var('rows'))
        fixed_values = request.session.get(self.get_session_var('fixed_values'))
        importer = self.importer_class()
        context = super(BaseImportProcessView, self).get_context_data()
        try:
            results = importer.import_rows(rows, fixed_values=fixed_values, commit=True)
            context["results"] = results
            context["import_success"] = True
            del request.session[self.get_session_var('rows')]
            return self.render_to_response(context)
        except:
            return redirect(self.request.path)
