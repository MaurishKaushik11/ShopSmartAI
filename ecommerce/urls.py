from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
    
    # Product views
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Cart views
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout views
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<uuid:order_id>/', views.order_success, name='order_success'),
    
    # AI recommendation endpoints
    path('interaction/<int:product_id>/', views.product_interaction, name='product_interaction'),
    path('api/recommendations/', views.get_recommendations, name='get_recommendations'),
]