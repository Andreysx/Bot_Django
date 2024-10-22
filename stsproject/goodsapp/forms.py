from django import forms


class ExcelUploadForm(forms.Form):
    """Форма загрузки файла(xlsx)"""
    file = forms.FileField(label='Выберите файл')
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
                           max_length=50, label='Название заказа', required=True)
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
                                  label='Описание заказа', required=True)
