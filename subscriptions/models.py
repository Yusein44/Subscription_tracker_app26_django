from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    BILLING_CHOICES = [
        ('monthly', 'Месечно'),
        ('yearly', 'Годишно'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="Име на услугата")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    currency = models.CharField(max_length=10, default="BGN")
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default='monthly')
    start_date = models.DateField(verbose_name="Дата на започване")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"

    def annual_cost(self):
        if self.billing_cycle == 'monthly':
            return self.price * 12
        return self.price