from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .import views

router =  DefaultRouter()
router.register('product',views.ProductViewSets,basename='product')
router.register('cart',views.CartView,basename='cart')
urlpatterns = [
     path('',include(router.urls)),
     path('orders/', views.OrderListView.as_view(), name="orders"),
     path('orders/<int:pk>/', views.OrderDetailView.as_view(), name="orders"),
]
