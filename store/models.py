from django.db import models
from django.urls import reverse
from s3direct.fields import S3DirectField

#Model : Category
class Category(models.Model):
    name = models.CharField(max_length=250,unique=True)
    slug = models.SlugField(max_length=250,unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category',blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_url(self):
        return reverse('product_by_category',args=[self.slug])


    def __str__(self):
        return self.name
#Model : Product
class Product(models.Model):
    name = models.CharField(max_length=250,unique=True)
    slug = models.SlugField(max_length=250,unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
   # image = models.ImageField(upload_to='product', blank=True)
    image = S3DirectField(dest='primary_destination', blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ('name',)
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

#Model : cart
class Cart(models.Model):
    cart_id = models.CharField(max_length=250,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.cart_id
    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.product
    class Meta:
        db_table = 'CartItem'
    def sub_total(self):
        return self.product.price * self.quantity

#Model : Order
class Order(models.Model):
    token = models.CharField(max_length=250,blank=True)
    total = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='USD Order Total')
    emailAddress = models.EmailField(max_length=250,blank=True,verbose_name='Email Address')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'Order'
        ordering = ['created']


class OrderItem(models.Model):
    product = models.CharField(max_length=250)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='USD Price')
    order = models.ForeignKey(Order,on_delete=models.CASCADE)

    class Meta:
        db_table = 'OrderItem'
    def sub_total(self):
        return self.quantity*self.price
    def _str_(self):
        return self.product



