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

        try:
            del self.request.session[self.get_session_var('hints')]
        except:
            pass
        try:
            del self.request.session[self.get_session_var('rows_status')]
        except:
            pass

        importer = self.importer_class()
        csv_file = form.cleaned_data.get('csv_file')
        #stream = TextIOWrapper(csv_file.file, encoding=self.request.encoding)
        stream = TextIOWrapper(csv_file.file, encoding="utf-8")
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

    def get_import_url(self):
        return self.import_url

    def get_context_data(self, *args, **kwargs):
        context = super(BaseImportProcessView, self).get_context_data(*args, **kwargs)
        context.update(self.template_context)
        context['import_url'] = self.get_import_url()
        return context

    def get_session_prefix(self):
        key = "%s" % self.importer_class.__class__.__name__
        return key

    def get_session_var(self, varname):
        return "%s_%s" % (self.get_session_prefix(), varname)

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get(self.get_session_var('rows')):
            return redirect(self.get_import_url())
        return super(BaseImportProcessView, self).dispatch(request, *args, **kwargs)

    def get_fixed_values(self, request):
        fixed_values = request.session.get(self.get_session_var('fixed_values'))
        return fixed_values

    def get(self, request, *args, **kwargs):
        rows = request.session.get(self.get_session_var('rows'))
        fixed_values = self.get_fixed_values(request)
        hints = request.session.get(self.get_session_var('hints'), {})
        importer = self.importer_class()
        results = importer.import_rows(rows, fixed_values=fixed_values, commit=False, hints=hints)
        self.request.session[self.get_session_var('rows_status')] = results['rows_status']

        context = self.get_context_data()
        context["results"] = results
        context["hints"] = hints
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        rows = request.session.get(self.get_session_var('rows'))
        rows_status = request.session.get(self.get_session_var('rows_status'))

        skip_lines = request.POST.getlist('skip_lines')
        hints = request.session.get(self.get_session_var('hints'), {})
        new_hints = { x : 'skip' for x in skip_lines }

        for key in request.POST:
            if key.startswith("hints_"):
                value = request.POST[key]
                line_no = key.replace("hints_", "")
                new_hints[line_no] = value

        hints.update(new_hints)


        self.request.session[self.get_session_var('hints')] = hints
        fixed_values = self.get_fixed_values(request)
        importer = self.importer_class()
        context = super(BaseImportProcessView, self).get_context_data()
        #TODO: commit should be set to True only if we don't have errors from the previous round
        try:
            results = importer.import_rows(rows, fixed_values=fixed_values, commit=True, hints=hints)
            context["results"] = results
            context["hints"] = hints
            context["import_success"] = True

            del request.session[self.get_session_var('rows')]
            del request.session[self.get_session_var('hints')]
            del request.session[self.get_session_var('rows_status')]
            return self.render_to_response(context)

        except Exception as e:
            return redirect(self.request.path)
