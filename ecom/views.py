from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated 
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView,RetrieveAPIView
from .models import Product,Cart,Order
from .serializers import ProductSerializer,CartSerializer,CartItemSerializer,AddItemToCartSerializer,OrderListSerializer,CreateOrderSerializer,OrderDetailSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

class ProductViewSets(viewsets.ModelViewSet):
    serializer_class =  ProductSerializer
    queryset =  Product.objects.all()


class CartView(viewsets.ModelViewSet):

    permission_classes =  (IsAuthenticated,)

    def list(self,request):
        obj,_ =  Cart.objects.get_or_create(user=request.user,ordered=False)

        serializer = CartSerializer(obj,context={'request':request})
        return Response(serializer.data)

        
    def get_queryset(self):
        return self.request.user.carts.get(ordered=False).items.all()

    def get_serializer_class(self):
        if self.action == "create":
            return AddItemToCartSerializer
        return CartItemSerializer


class OrderListView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.orders.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderListSerializer

class OrderDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class =  OrderDetailSerializer

    def get_queryset(self):
        return self.request.user.orders.all()