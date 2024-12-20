from django.urls import path
from .views import OrderListCreateView, OrderDetailView

urlpatterns = [
    path('orders', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:order_id>', OrderDetailView.as_view(), name='order-detail'),
]