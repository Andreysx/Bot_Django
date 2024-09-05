from django.shortcuts import render, get_object_or_404, redirect
from .models import Orders, Products


# Create your views here.

def index(request):
    orders = Orders.objects.all()
    return render(request, 'goods/index.html', {'all_orders': orders})


def order_review(request):
    pass
