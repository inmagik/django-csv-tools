from django import forms

class BaseCSVImportForm(forms.Form):
    csv_file = forms.FileField()

    
