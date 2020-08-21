from rest_framework import serializers
from .models import Product,CartItem,Cart,Product,ReciverInfo,Order
from django.db.models import F



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id','name','price','image')

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('cart',)

    def get_total_price(self,obj):
        return obj.total_price


class AddItemToCartSerializer(serializers.ModelSerializer):
    cart_items_count = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('product','cart_items_count')

    def create(self,validated_data):
        user =  self.context.get('request').user
        product = self.validated_data.get('product')
        cart, _ = Cart.objects.get_or_create(user=user,ordered=False)
        cart_item = CartItem.objects.filter(
            cart = cart,product = product
        )
        if cart_item.exists():
            cart_item =  cart_item.first()
            if product.quantity > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
           

            return cart_item
        
        cart_item = CartItem.objects.create(
            cart = cart,product=product
        )
        cart.items.add(cart_item)
        return cart_item

    def get_cart_items_count(self,obj):
        user =  self.context.get('request').user
        return user.carts.get(ordered=False).items.count()


class CartSerializer(serializers.ModelSerializer):
    total_price =  serializers.SerializerMethodField()
    items_count =  serializers.SerializerMethodField()
    items =  CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields =  '__all__'

    def get_total_price(self,obj):
        return obj.total_price

    def get_items_count(self,obj):
        return obj.items_count


# Order

class ReciverInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReciverInfo
        fields = '__all__'

class OrderListSerializer(serializers.ModelSerializer):
    total_price =  serializers.SerializerMethodField()
    items_count =  serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id','created_at','total_price','code',
        'items_count','shipping_status','purchase_invoice')

    def get_total_price(self,obj):
        total_price = 0
        for item in obj.cart.items.all():
            total_price += item.total_price
        return total_price

    def get_items_count(self,obj):
        return obj.cart.items.all().count()

class OrderDetailSerializer(serializers.ModelSerializer):
    cart =  CartSerializer()
    reciver = ReciverInfoSerializer()

    class Meta:
        model =  Order
        fields = '__all__'

class CreateOrderSerializer(serializers.ModelSerializer):
    reciver = ReciverInfoSerializer()

    class Meta:
        model = Order
        exclude = ('code',)
        read_only_fields = (
            'shipping_status','cart','user','shipping_method',
        )

    # def create(self,data):
    #     user =  self.context.get('request').user
       
    #     cart =  user.carts.get(ordered=False)

    #     if cart.items.all().exists() == False:
    #         raise serializers.ValidationError('Cart must not be empty')

    #     for item in cart.items.all():
    #         Product.objects.filter(id=item.product.id).update(
    #             sale_count = F('sale_count') + item.quantity
    #         )

    #     reciver_info =  ReciverInfo.objects.create(**data.get('reciver'))

    #     cart.ordered = True
    #     cart.save()
        
    #     order =  Order.objects.create(
    #         user=user,reciver=reciver_info,cart=cart,
    #         purchase_invoice=data.get('purchase_invoice'),
    #         shipping_status="OrderConfirm"
    #     )

    #     Cart.objects.create(user=user)
    #     return Order
    def create(self, data):
        user = self.context.get('request').user
        cart = user.carts.get(ordered=False)
        # Validate cart
        if cart.items.all().exists() == False:
            raise serializers.ValidationError("Cart must not be empty")
        # Update products sale count
        for item in cart.items.all():
            Product.objects.filter(id=item.product.id).update(
                sale_count=F('sale_count') + item.quantity
            )
        # Create reaciver info model
        reciver_info = ReciverInfo.objects.create(**data.get('reciver'))
        # Create order model
        cart.ordered = True
        cart.save()
        order = Order.objects.create(
            user=user, cart=cart, reciver=reciver_info,
            purchase_invoice=data.get('purchase_invoice'), shipping_status="Preparation"
        )
        # Create another cart model with ordered=False
        Cart.objects.create(user=user)
        return order


