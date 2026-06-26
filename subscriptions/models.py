from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Име на компанията")
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=5000.00, verbose_name="Бюджет")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100, verbose_name="Име на отдел (напр. Маркетинг)")

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Собственик / Мениджър'),
        ('employee', 'Служител'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class Subscription(models.Model):
    BILLING_CHOICES = [
        ('monthly', 'Месечно'),
        ('yearly', 'Годишно'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Кой ползва софтуера")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=200, verbose_name="Име на софтуера (напр. AWS, Slack)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    currency = models.CharField(max_length=10, default="USD") 
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default='monthly')
    start_date = models.DateField(verbose_name="Дата на подновяване")
    
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True, verbose_name="Фактура (PDF/Снимка)")
    is_ai_extracted = models.BooleanField(default=False, verbose_name="Прочетено от AI?")
    ai_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Точност на AI (%)")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency} ({self.company.name})"

    def annual_cost(self):
        if self.billing_cycle == 'monthly':
            return self.price * 12
        return self.price