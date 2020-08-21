from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# from ecommerce import utils
import string
import random


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Product(models.Model):
    name = models.CharField(max_length=100,blank=False)
    price = models.PositiveIntegerField()
    image = models.ImageField(default='default.jpg',upload_to='images')
    quantity = models.PositiveIntegerField(blank=True,null=True)
    sale_count = models.IntegerField(default=0,blank=True,null=True)
    def __str__(self):
        return self.name



class CartItem(models.Model):
    cart =  models.ForeignKey('Cart',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="carts")
    items = models.ManyToManyField(CartItem,related_name='items')
    ordered = models.BooleanField(default=False)
    created_at =  models.DateTimeField(auto_now_add=True)

    class Meta():
        ordering = ('-created_at',)

    def __str__(self):
        return self.user.username

    @property
    def total_price(self):
        total_price=0
        for item in self.items.all():
            total_price += int(item.total_price)
        return total_price

    @property
    def items_count(self):
        return self.items.all().count()




@receiver(post_save,sender=User)
def create_cart(sender,instance,created,**kwargs):
    if created:
        Cart.objects.create(user=instance)


class ReciverInfo(models.Model):
    full_name =  models.CharField(max_length=100)
    phone_number =  models.PositiveIntegerField()
    address =  models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.full_name

class Order(models.Model):
    user =  models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name="orders")
    reciver =  models.ForeignKey(ReciverInfo,on_delete=models.DO_NOTHING)
    cart =  models.ForeignKey(Cart,on_delete=models.DO_NOTHING)
    purchase_invoice = models.BooleanField(default=False)
    shipping_status = models.CharField(max_length=50)
    code =  models.CharField(max_length=8,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user} - {self.code}"

    def save(self,*args,**kwargs):
        self.code = id_generator()
        super(Order,self).save(*args,**kwargs)

    