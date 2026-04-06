from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_subscription, name='add_subscription'),
    path('edit/<int:pk>/', views.edit_subscription, name='edit_subscription'),
    path('cancel/<int:pk>/', views.cancel_subscription, name='cancel_subscription'),
]