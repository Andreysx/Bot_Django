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

            # Обновляем статус найденных продуктов
            for product in products:
                product.is_done = True
                product.save()  # Сохраняем изменения в БД

            # Обновляем статус заказа
            order.update_status()

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
    Загрузка excel файла(БЕЗ ШАПКИ) только авторизованным пользователем, парсинг и добавление в БД
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Получаем загруженный файл
            uploaded_file = request.FILES['file']

            # Проверяем расширение файла
            if not uploaded_file.name.endswith('.xlsx'):
                messages.error(request, "Пожалуйста, загрузите файл с расширением .xlsx.")
                return redirect('goodsapp:upload_order')  # Перенаправление на страницу загрузки

            # Сохранение нового заказа
            order = Orders.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                author=request.user
            )

            # Обработка Excel файла без указания заголовков
            df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)

            # Поиск строки с заголовками
            header_row_index = None
            for i, row in df.iterrows():
                if 'No. / №' in row.values:  # Замените на нужное название столбца
                    header_row_index = i
                    break

            if header_row_index is not None:
                # Устанавливаем заголовки и отсекаем лишние строки
                df.columns = df.iloc[header_row_index]
                df = df[header_row_index + 1:]  # Начинаем с строки после заголовков

                products_to_create = []
                for i, row in df.iterrows():
                    products_to_create.append(Products(
                        order=order,
                        article=str(row.iloc[1]),  # Укажите нужные названия столбцов
                        name=row.iloc[2],
                        quantity=row.iloc[5],
                        unit_price=row.iloc[6],
                        amount=row.iloc[9],
                        weight=row.iloc[7],
                    ))

                Products.objects.bulk_create(products_to_create)  # Создание объектов за один раз

                return redirect('goodsapp:order_review', order.id)

            else:
                messages.error(request, "Не найдены заголовки в файле.")
                return redirect('goodsapp:index')  # Перенаправление на главную страницу или другую страницу

    else:
        form = ExcelUploadForm()

    return render(request, 'goods/upload.html', {'form': form})


@login_required
def delete_product(request, product_id):
    """Удаление продукта из заказа"""
    product = get_object_or_404(Products, pk=product_id)

    # Проверка, что текущий пользователь является автором заказа
    if product.order.author != request.user:
        messages.error(request, "У вас нет прав на удаление этого продукта.")
        return redirect('goodsapp:index')  # Перенаправление на главную страницу

    if request.method == 'POST':
        product.delete()  # Удаление продукта
        messages.success(request, 'Продукт успешно удален.')  # Сообщение об успешном удалении
        return redirect('goodsapp:order_review', product.order.id)

    return render(request, 'goods/confirm_delete_product.html', {'product': product})

@login_required
def confirm_delete_order(request, order_id):
    order = get_object_or_404(Orders, pk=order_id)

    # Проверка, что текущий пользователь является автором заказа
    if order.author != request.user:
        messages.error(request, "У вас нет прав на удаление этого заказа.")
        return redirect('goodsapp:index')  # Перенаправление на главную страницу

    if request.method == 'POST':
        order.delete()  # Удаление заказа
        messages.success(request, 'Заказ успешно удален.')  # Сообщение об успешном удалении
        return redirect('goodsapp:index')  # Перенаправление на главную страницу

    return render(request, 'goods/confirm_delete.html', {'order': order})