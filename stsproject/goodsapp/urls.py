from django.urls import path
from .views import index, order_review

app_name = 'goodsapp'

urlpatterns = [
    path('', index, name='index'),
    path('order_review/<int:order_id>/', order_review, name='order_review')
]