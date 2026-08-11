from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
