from django.db import models
from django.contrib.auth.models import User


class Orders(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}, {self.date}, {self.is_done}"

    def update_status(self):
        """Обновление статуса заказа на 'Завершен', если все продукты отмечены как 'Отмечены'."""
        if all(product.is_done for product in self.products.all()):
            self.is_done = True
        else:
            self.is_done = False
        self.save()

class Products(models.Model):
    article = models.CharField(max_length=80,blank=False)
    name = models.CharField(max_length=80)
    quantity = models.CharField(max_length=80)
    unit_price = models.CharField(max_length=80)
    weight = models.CharField(max_length=80)
    amount = models.CharField(max_length=80,null=True)
    is_done = models.BooleanField(default=False)
    order = models.ForeignKey(Orders,related_name='products',on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.article} | {self.name} | {self.is_done} | {self.order}"
