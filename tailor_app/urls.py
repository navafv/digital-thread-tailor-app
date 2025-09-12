# tailor_app/urls.py
from django.urls import path
from . import views

app_name = 'tailor_app'

urlpatterns = [
    # Dashboard & Reports
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports_view, name='reports'),

    # Customer URLs - Standardized to use 'customer_id'
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/invite/', views.invite_customer_to_portal, name='invite_customer_to_portal'),
    
    # Order URLs - Standardized to use 'customer_id' and 'order_id'
    path('customers/<int:customer_id>/add_order/', views.add_order, name='add_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('orders/<int:order_id>/invoice/', views.generate_pdf_invoice, name='generate_pdf_invoice'),

    # Measurement URLs - Standardized to use 'customer_id' and 'measurement_id'
    path('customers/<int:customer_id>/add_measurement/', views.add_measurement, name='add_measurement'),
    path('measurements/<int:measurement_id>/edit/', views.edit_measurement, name='edit_measurement'),
    path('measurements/<int:measurement_id>/delete/', views.delete_measurement, name='delete_measurement'),
    
    # Calendar & Appointments
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar-events/', views.calendar_events_api, name='calendar_events_api'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:appointment_id>/update/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),

    # Inventory & Supplier
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/<int:item_id>/edit/', views.edit_inventory_item, name='edit_inventory_item'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),

    # Workflow & Tasks
    path('workflows/', views.workflow_template_list, name='workflow_list'),
    path('workflows/new/', views.create_workflow_template, name='create_workflow'),
    path('workflows/<int:template_id>/edit/', views.edit_workflow_template, name='edit_workflow'),
    path('orders/<int:order_id>/apply-workflow/', views.apply_workflow_to_order, name='apply_workflow'),
    path('tasks/<int:task_id>/update/', views.update_order_task_status, name='update_task'),
]

