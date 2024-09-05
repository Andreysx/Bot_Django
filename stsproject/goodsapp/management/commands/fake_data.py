from random import choice, randint

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from goodsapp.models import Orders, Products


class Command(BaseCommand):
    help = "Generate fake orders and products."

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of orders to create')

    def handle(self, *args, **kwargs):
        count = kwargs.get('count')

        # Получаем всех пользователей из базы данных
        authors = User.objects.all()
        if not authors.exists():
            self.stdout.write(self.style.ERROR("No users found in the database. Please create a user first."))
            return

        # Генерируем заказы и продукты
        for i in range(1, count + 1):
            author = choice(authors)  # Случайно выбираем автора
            order = Orders(
                name=f'Name{i} from order {author.username}',  # Используем имя пользователя
                description=f"Description{i}",
                author=author  # Устанавливаем автора
            )
            order.save()
            self.stdout.write(self.style.SUCCESS(f"Created order {order.id} by {author.username}"))

            # Генерируем продукты для каждого заказа
            for j in range(1, count + 1):
                product = Products(
                    article=j,  # Используем j как номер статьи
                    name=f'Name{j} from order {order.id}',
                    quantity=randint(1, 10),  # Случайное количество
                    unit_price=randint(100, 1000),  # Случайная цена за единицу
                    weight=randint(1, 5),  # Случайный вес
                    amount=None,  # Или установите значение, если нужно
                    order=order  # Устанавливаем связь с заказом
                )
                product.save()
                self.stdout.write(self.style.SUCCESS(f"Created product {product.id} for order {order.id}"))

