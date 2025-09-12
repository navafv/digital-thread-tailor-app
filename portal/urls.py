# portal/urls.py
from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.portal_dashboard, name='dashboard'),
    path('orders/', views.portal_order_list, name='order_list'),
    path('orders/<int:pk>/', views.portal_order_detail, name='order_detail'),
    path('profile/', views.portal_profile, name='profile'),
    path('appointments/request/', views.request_appointment, name='request_appointment'),
]
