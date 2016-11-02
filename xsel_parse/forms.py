from django import forms


class UploadForm2(forms.Form):
    file_field = forms.FileField(label='Выберите файл:', widget=forms.FileInput(attrs={'class': 'btn btn-default'}))


class TextToFileForm(forms.Form):
    text_field = forms.CharField()
    file_name = forms.CharField(max_length=30)

class UploadForm3(forms.Form):
    file_field = forms.FileField(label='Выберите файл:', widget=forms.FileInput(attrs={'class': 'btn btn-default'}))