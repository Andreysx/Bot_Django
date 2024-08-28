from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Orders(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}, {self.date}, {self.is_done}"

class Products(models.Model):
    article = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=80, blank=False)
    quantity = models.IntegerField(blank=False, null=False)
    unit_price = models.IntegerField(blank=False, null=False)
    weight = models.IntegerField(blank=False, null=False)
    amount = models.IntegerField(blank=False, null=False)
    is_done = models.BooleanField(default=False)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.article} | {self.name} | {self.is_done} | {self.order}"
