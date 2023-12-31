from django.urls import path
from Order.views import GetOrderAPIView, CreateOrderAPIView, \
    UpdateOrderAPIView, GetOrdersByUserAPIView, GetOrderByPkAPIView

app_name = 'Order'

urlpatterns = [
    path('get_orders/<user>/', GetOrdersByUserAPIView.as_view()),
    path('get_order/<user>/<furniture_pk>/<description>/<status>/<completed>/', GetOrderAPIView.as_view()),
    path('create_order/', CreateOrderAPIView.as_view()),
    path('update_order/<pk>/', UpdateOrderAPIView.as_view()),
    path('get_order_by_pk/<order_pk>/', GetOrderByPkAPIView.as_view()),
]