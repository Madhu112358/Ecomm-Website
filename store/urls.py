
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name='home'),
    path('category/<slug:category_slug>',views.home,name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>',views.productpage,name='product_detail'),
    path('cart/add/<int:product_id>',views.add_cart, name='add_cart'),
    path('cart',views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:product_id>',views.remove_cart, name='remove_cart'),
    path('cart/delete/<int:product_id>',views.delete_cart, name='delete_cart'),
    path('thankyou/<int:order_id>',views.thanks_page, name='thanks_page')
]
