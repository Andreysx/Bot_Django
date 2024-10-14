from django import forms


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Выберите файл')
    name = forms.CharField(max_length=50, label='Название заказа', required=True)
    description = forms.CharField(widget=forms.Textarea, label='Описание заказа', required=True)