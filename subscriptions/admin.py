from django.contrib import admin
from .models import Company, Department, UserProfile, Subscription

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_budget', 'created_at')
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role')
    list_filter = ('role', 'company')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'price', 'currency', 'billing_cycle', 'is_active', 'is_ai_extracted')

    list_filter = ('company', 'is_active', 'billing_cycle', 'is_ai_extracted')

    search_fields = ('name', 'company__name')