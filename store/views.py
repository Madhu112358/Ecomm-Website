from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Category,Cart,CartItem,Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.http import HttpResponse

def home(request,category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page  = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=category_page, available = 'True')
    else:
        products = Product.objects.filter(available='True')
    return render(request, 'store/home.html', {'category': category_page,'allproducts': products})

def productpage(request,category_slug,product_slug):
    try:
        products = Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise  e
    return render(request,'store/product.html',{'product': products})

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    product= Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart
        )
    cart_item.save()
    return redirect('cart_detail')

def cart_detail(request,total=0,counter=0,cart_items=None):
    try:
        cart = Cart.objects.get(cart_id =_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    stripe_total = int(total * 100)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        token = request.POST['stripeToken']
        email = request.POST['stripeEmail']
        try:
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='usd',
                description='MadhuJay Store',
                source=token
                #customer = email
            )
            try:
                order_details = Order.objects.create(
                    token = token,
                    total = total,
                    emailAddress = email,
                )
                order_details.save()
                for order_item in cart_items:
                    or_item = OrderItem.objects.create(
                        product = order_item.product.name,
                        quantity = order_item.quantity,
                        price = order_item.product.price,
                        order = order_details
                    )
                    or_item.save()

                    #reduce stock
                    products = Product.objects.get(id=order_item.product.id)
                    products.stock = int(order_item.product.stock - order_item.quantity)
                    products.save()
                    order_item.delete()

                    #print a message when order is created
                    print('the order has been created')
                return redirect('thanks_page',order_details.id)
            except ObjectDoesNotExist:
                pass
        except stripe.error.CardError as e:
            return False,e

    return render(request,'store/cart.html',dict(cart_items= cart_items,total=total,counter=counter,publishable_key=stripe_publishable_key,
                                                 stripe_total=stripe_total,stripe_api_key=stripe.api_key))



def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product= get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

def delete_cart(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')

def thanks_page(request,order_id):
    if order_id:
        customer_order = get_object_or_404(Order, id = order_id)
    return render(request,'store/thankyou.html',{'customer_order':customer_order})

