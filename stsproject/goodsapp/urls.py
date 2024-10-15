from django.urls import path
from .views import index, order_review, search_product, upload_order,confirm_delete_order,upload_order_view

app_name = 'goodsapp'
# пространство имен включается в тег url в шаблоне

urlpatterns = [
    path('', index, name='index'),
    path('order_review/<int:order_id>/', order_review, name='order_review'),
    path('orders/<int:order_id>/search', search_product, name='search_product'),
    path('upload/', upload_order_view, name='upload_order'),
    # path('order/<int:order_id>/delete/', delete_order, name='delete_order'),
    path('order/<int:order_id>/confirm-delete/', confirm_delete_order, name='confirm_delete_order'),
]
