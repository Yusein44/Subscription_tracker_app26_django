from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_subscription, name='add_subscription'),
    path('edit/<int:pk>/', views.edit_subscription, name='edit_subscription'),
    path('cancel/<int:pk>/', views.cancel_subscription, name='cancel_subscription'),
    path('login/', auth_views.LoginView.as_view(template_name='subscriptions/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
]