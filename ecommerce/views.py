from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json
import logging

from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserInteraction
from .recommendation_service import recommendation_service

logger = logging.getLogger(__name__)

def get_or_create_cart(request):
    """Get or create cart for session"""
    if not request.session.session_key:
        request.session.create()
    
    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key
    )
    return cart

@ensure_csrf_cookie
def home(request):
    """Homepage with featured products and recommendations"""
    # Get featured products
    featured_products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:8]
    
    # Get categories
    categories = Category.objects.all()[:6]
    
    # Get personalized recommendations if session exists
    recommendations = []
    if request.session.session_key:
        recommendations = recommendation_service.get_user_recommendations(
            request.session.session_key, n_recommendations=4
        )
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'recommendations': recommendations,
        'cart': get_or_create_cart(request)
    }
    return render(request, 'ecommerce/home.html', context)

@ensure_csrf_cookie
def product_list(request, category_slug=None):
    """Display products with filtering and pagination"""
    products = Product.objects.filter(is_active=True)
    category = None
    
    # Filter by category if provided
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'categories': Category.objects.all(),
        'query': query,
        'sort_by': sort_by,
        'cart': get_or_create_cart(request)
    }
    return render(request, 'ecommerce/product_list.html', context)

@ensure_csrf_cookie
def product_detail(request, slug):
    """Display product details with recommendations"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Record view interaction
    if request.session.session_key:
        recommendation_service.record_interaction(
            request.session.session_key, 
            product.id, 
            'view'
        )
    
    # Get similar products
    similar_products = recommendation_service.get_similar_products(
        product.id, n_recommendations=4
    )
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'cart': get_or_create_cart(request)
    }
    return render(request, 'ecommerce/product_detail.html', context)

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart via AJAX"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        
        quantity = int(request.POST.get('quantity', 1))
        
        # Check stock
        if quantity > product.stock:
            return JsonResponse({
                'success': False, 
                'error': 'Not enough stock available'
            })
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return JsonResponse({
                    'success': False, 
                    'error': 'Not enough stock available'
                })
            cart_item.save()
        
        return JsonResponse({
            'success': True, 
            'cart_total': cart.get_total_cost(),
            'cart_items': cart.get_total_items()
        })
        
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to add to cart'})

@ensure_csrf_cookie
def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    
    # Get recommendations based on cart items
    recommendations = []
    if request.session.session_key:
        recommendations = recommendation_service.get_user_recommendations(
            request.session.session_key, n_recommendations=4
        )
    
    context = {
        'cart': cart,
        'recommendations': recommendations
    }
    return render(request, 'ecommerce/cart.html', context)

@require_POST
def update_cart(request, item_id):
    """Update cart item quantity"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False, 
                    'error': 'Not enough stock available'
                })
            cart_item.quantity = quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True, 
            'cart_total': cart.get_total_cost(),
            'cart_items': cart.get_total_items()
        })
        
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to update cart'})

@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return JsonResponse({
            'success': True, 
            'cart_total': cart.get_total_cost(),
            'cart_items': cart.get_total_items()
        })
        
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to remove item'})

def checkout(request):
    """Checkout page"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('ecommerce:cart')
    
    if request.method == 'POST':
        try:
            # Create order
            order = Order.objects.create(
                session_key=request.session.session_key,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                address=request.POST.get('address'),
                postal_code=request.POST.get('postal_code'),
                city=request.POST.get('city')
            )
            
            # Create order items and record purchase interactions
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
                
                # Record purchase interaction
                recommendation_service.record_interaction(
                    request.session.session_key,
                    cart_item.product.id,
                    'purchase'
                )
                
                # Update stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Order {order.order_id} placed successfully!')
            return redirect('ecommerce:order_success', order_id=order.order_id)
            
        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
            messages.error(request, 'Error processing your order. Please try again.')
    
    context = {'cart': cart}
    return render(request, 'ecommerce/checkout.html', context)

def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, order_id=order_id)
    
    context = {'order': order}
    return render(request, 'ecommerce/order_success.html', context)

@csrf_exempt
@require_POST
def product_interaction(request, product_id):
    """Record user interaction (like/dislike) with product"""
    try:
        if not request.session.session_key:
            request.session.create()
        
        data = json.loads(request.body)
        interaction_type = data.get('type')
        
        if interaction_type not in ['like', 'dislike']:
            return JsonResponse({'success': False, 'error': 'Invalid interaction type'})
        
        success = recommendation_service.record_interaction(
            request.session.session_key,
            product_id,
            interaction_type
        )
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to record interaction'})
            
    except Exception as e:
        logger.error(f"Error recording interaction: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error'})

@require_GET
def get_recommendations(request):
    """Get personalized recommendations via AJAX"""
    try:
        if not request.session.session_key:
            return JsonResponse({'recommendations': []})
        
        recommendations = recommendation_service.get_user_recommendations(
            request.session.session_key, 
            n_recommendations=int(request.GET.get('count', 5))
        )
        
        rec_data = []
        for rec in recommendations:
            rec_data.append({
                'id': rec['product'].id,
                'name': rec['product'].name,
                'price': float(rec['product'].price),
                'image_url': rec['product'].image_url,
                'slug': rec['product'].slug,
                'score': rec['score'],
                'reason': rec['reason']
            })
        
        return JsonResponse({'recommendations': rec_data})
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return JsonResponse({'recommendations': []})
