# tailor_app/urls.py

from django.urls import path
from . import views

app_name = 'tailor_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports_view, name='reports'),

    # Chart Data URL
    path('api/monthly-revenue/', views.get_monthly_revenue_data, name='monthly_revenue_data'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_pk>/invite/', views.invite_customer_to_portal, name='invite_customer'),

    # Order URLs
    path('customers/<int:customer_pk>/orders/add/', views.add_order, name='add_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.edit_order, name='edit_order'),
    
    # Measurement URLs
    path('customers/<int:customer_pk>/measurements/add/', views.add_measurement, name='add_measurement'),
    path('measurements/<int:pk>/edit/', views.edit_measurement, name='edit_measurement'),
    path('measurements/<int:pk>/delete/', views.delete_measurement, name='delete_measurement'),

    # PDF Invoice URL
    path('orders/<int:order_pk>/invoice/pdf/', views.generate_pdf_invoice, name='generate_pdf_invoice'),

    # Calendar URLs
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/add/', views.add_appointment, name='add_appointment'),
    path('api/calendar-events/', views.calendar_events_api, name='calendar_events_api'),
    path('appointments/<int:appointment_id>/update/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),

    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/<int:item_id>/edit/', views.edit_inventory_item, name='edit_inventory_item'),

    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
]

