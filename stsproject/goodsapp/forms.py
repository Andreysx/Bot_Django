from django import forms


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Выберите файл')
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название заказа'}),
                           max_length=50, label='Название заказа', required=True)
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
                                  label='Описание заказа', required=True)
