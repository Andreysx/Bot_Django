from django import forms


class ExcelUploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Загрузите файл'}))
