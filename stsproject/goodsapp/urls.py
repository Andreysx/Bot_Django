from django.urls import path
from .views import index

app_name = 'goodsapp'

urlpatterns = [
    path('', index, name='index')
]