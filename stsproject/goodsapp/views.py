from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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


def upload_order_view(request):
    """
     Добавление проверки авторизации
    :param request:
    :return:
    """
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в систему для загрузки файла.")
        return redirect('login')  # Убедитесь, что здесь указан правильный URL для страницы входа

    return upload_order(request)  # Вызов оригинального представления для загрузки файла

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
                name=form.cleaned_data['name'],  # Используем название из формы
                description=form.cleaned_data['description'],  # Используем описание из формы
                author=request.user
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
def confirm_delete_order(request, order_id):
    order = get_object_or_404(Orders, pk=order_id)

    # Проверка, что текущий пользователь является автором заказа
    if order.author != request.user:
        return redirect('goodsapp:index')  # Перенаправление на главную страницу, если не автор

    if request.method == 'POST':
        order.delete()  # Удаление заказа
        messages.success(request, 'Заказ успешно удален.')  # Сообщение об успешном удалении используя Django Messages Framework
        return redirect('goodsapp:index')  # Перенаправление на главную страницу

    return render(request, 'goods/confirm_delete.html', {'order': order})