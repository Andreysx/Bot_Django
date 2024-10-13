from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Orders, Products
from .forms import ExcelUploadForm
import pandas as pd



# Create your views here.

def index(request):
    """ Начальная страница"""
    orders = Orders.objects.all()

    # Поиск по имени заказа
    query = request.GET.get('q')
    if query:
        orders = orders.filter(name__icontains=query)  # Фильтрация по имени заказа

    # Сортировка по дате
    sort_by = request.GET.get('sort')
    if sort_by == 'date':
        orders = orders.order_by('date')  # Сортировка по возрастанию даты
    elif sort_by == 'date_desc':
        orders = orders.order_by('-date')  # Сортировка по убыванию даты

    return render(request, 'goods/index.html', {'all_orders': orders})


def order_review(request, order_id):
    """Обзор содержания заказа - продуктов в нем"""
    order = get_object_or_404(Orders, pk=order_id)
    products = order.products.all()
    return render(request, 'goods/order_review.html', {'order': order, 'products': products})

def search_product(request, order_id):
    """Поиск продукта по артиклу"""
    order = get_object_or_404(Orders, pk=order_id)
    products = Products.objects.filter(order=order)  # Получаем все продукты для этого заказа

    if request.method == 'GET':
        article = request.GET.get('article')
        if article:
            products = products.filter(article=article)  # Фильтруем по полю article

    return render(request, 'goods/search_results.html', {'order': order, 'products': products})


@login_required
def upload_order(request):
    """
    Загрузка excel файла(БЕЗ ШАПКИ) только авторизованным пользователем, парсинг и добавление  в бд
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохранение нового заказа
            order = Orders.objects.create(
                name="Новый заказ",  # Вы можете задать имя заказа по своему усмотрению
                description="Загружено из Excel",
                author=request.user  # Устанавливаем текущего пользователя как автора заказа
            )

            # Обработка Excel файла
            df = pd.read_excel(form.cleaned_data['file'], engine='openpyxl')

            # Предположим, что данные начинаются с первой строки и у вас есть следующие столбцы:
            # 'article', 'name', 'quantity', 'unit_price', 'weight'

            products_to_create = []
            for i, row in df.iterrows():
                # Products.objects.create(
                #     order=order,
                #     article=row['article'],  # Укажите нужные столбцы из вашего Excel файла
                #     name=row['name'],
                #     quantity=row['quantity'],
                #     unit_price=row['unit_price'],
                #     weight=row['weight']
                # )
                Products.objects.create(
                    order=order,
                    article=str(row.iloc[1]),  # Укажите нужные столбцы из вашего Excel файла
                    name=row.iloc[2],
                    quantity=row.iloc[5],
                    unit_price=row.iloc[6],
                    amount=row.iloc[9],
                    weight=row.iloc[7],
                    # eng_name=row.iloc[3]
                )

                Products.objects.bulk_create(products_to_create) # создание объектов за один раз

            return redirect('goodsapp:order_review', order.id)  # Перенаправление на список заказов после загрузки
    else:
        form = ExcelUploadForm()

    return render(request, 'goods/upload.html', {'form': form})


@login_required
def delete_order(request, order_id):
    """
    Удаление файла excel(Заказа) именно тем пользователем что загрузил его
    :param request:
    :param order_id:
    :return:
    """
    order = get_object_or_404(Orders, pk=order_id)

    # Проверка, что текущий пользователь является автором заказа
    if order.author == request.user:
        order.delete()  # Удаление заказа
        return redirect('goodsapp:index')  # Перенаправление на главную страницу
    else:
        # Можно добавить сообщение об ошибке или перенаправить на другую страницу
        return redirect('goodsapp:index')  # Перенаправление на главную страницу