from django.urls import path
from . import views

urlpatterns = [
    # Dashboard URL (NEW - This is now the homepage)
    path('', views.dashboard, name='dashboard'),

    # Customer URLs (The list is now at /customers/)
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    
    # Order URLs
    path('customer/<int:customer_pk>/order/add/', views.add_order, name='add_order'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/edit/', views.edit_order, name='edit_order'),

    # Measurement URLs
    path('customer/<int:customer_pk>/measurement/add/', views.add_measurement, name='add_measurement'),
    path('measurement/<int:pk>/edit/', views.edit_measurement, name='edit_measurement'),
    path('measurement/<int:pk>/delete/', views.delete_measurement, name='delete_measurement'),
]

