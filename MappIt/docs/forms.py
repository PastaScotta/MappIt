from django import forms

class UploadFileForm(forms.Form):
    table_name = forms.CharField()
    file = forms.FileField()
