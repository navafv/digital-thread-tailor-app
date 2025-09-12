from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/<int:pk>/edit/', views.edit_customer, name='edit_customer'),

    # Order URLs
    path('customer/<int:customer_pk>/add_order/', views.add_order, name='add_order'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/edit/', views.edit_order, name='edit_order'),

    # Order Image URL
    path('order_image/<int:pk>/delete/', views.delete_order_image, name='delete_order_image'),

    # Measurement URLs
    path('customer/<int:customer_pk>/add_measurement/', views.add_measurement, name='add_measurement'),
    path('measurement/<int:pk>/edit/', views.edit_measurement, name='edit_measurement'),
    path('measurement/<int:pk>/delete/', views.delete_measurement, name='delete_measurement'),
]

