import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from ecommerce.models import Category, Product

class Command(BaseCommand):
    help = 'Populate the database with sample e-commerce data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database with sample data...'))
        
        # Create Categories
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Latest gadgets, smartphones, laptops, and electronic accessories'
            },
            {
                'name': 'Home & Garden',
                'description': 'Furniture, home decor, garden tools, and household items'
            },
            {
                'name': 'Books & Media',
                'description': 'Books, eBooks, audiobooks, movies, and educational content'
            },
            {
                'name': 'Fashion & Beauty',
                'description': 'Clothing, shoes, accessories, cosmetics, and beauty products'
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Exercise equipment, sports gear, outdoor activities, and fitness accessories'
            },
            {
                'name': 'Health & Wellness',
                'description': 'Vitamins, supplements, personal care, and wellness products'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')

        # Create Products
        products_data = [
            # Electronics
            {
                'name': 'Smartphone Pro Max 256GB',
                'description': 'Latest flagship smartphone with advanced AI camera, 5G connectivity, and all-day battery life. Perfect for professionals and tech enthusiasts.',
                'price': 999.99,
                'category': 'Electronics',
                'stock': 50,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400'
            },
            {
                'name': 'Wireless Noise-Canceling Headphones',
                'description': 'Premium over-ear headphones with active noise cancellation, 30-hour battery, and studio-quality sound.',
                'price': 299.99,
                'category': 'Electronics',
                'stock': 75,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'
            },
            {
                'name': 'Ultra-Portable Laptop 14"',
                'description': 'Lightweight laptop with powerful processor, 16GB RAM, 512GB SSD. Ideal for work and creative projects.',
                'price': 1299.99,
                'category': 'Electronics',
                'stock': 30,
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400'
            },
            {
                'name': 'Smart Watch Series X',
                'description': 'Advanced fitness tracking, heart rate monitoring, GPS, and smartphone integration in a sleek design.',
                'price': 399.99,
                'category': 'Electronics',
                'stock': 100,
                'image_url': 'https://images.unsplash.com/photo-1544117519-31a4b719223d?w=400'
            },
            
            # Home & Garden
            {
                'name': 'Modern Ergonomic Office Chair',
                'description': 'Comfortable office chair with lumbar support, adjustable height, and breathable mesh back. Perfect for remote work.',
                'price': 249.99,
                'category': 'Home & Garden',
                'stock': 40,
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400'
            },
            {
                'name': 'Smart Home Security Camera',
                'description': '4K security camera with night vision, motion detection, and smartphone alerts. Keep your home safe.',
                'price': 179.99,
                'category': 'Home & Garden',
                'stock': 60,
                'image_url': 'https://images.unsplash.com/photo-1558618047-b37dfe96c51b?w=400'
            },
            {
                'name': 'Bamboo Kitchen Utensil Set',
                'description': 'Eco-friendly 12-piece bamboo kitchen utensil set with holder. Sustainable and stylish cooking tools.',
                'price': 34.99,
                'category': 'Home & Garden',
                'stock': 120,
                'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400'
            },
            
            # Books & Media
            {
                'name': 'The Art of AI Programming',
                'description': 'Comprehensive guide to artificial intelligence and machine learning programming. Perfect for developers and students.',
                'price': 49.99,
                'category': 'Books & Media',
                'stock': 200,
                'image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400'
            },
            {
                'name': 'Premium Audiobook Collection',
                'description': 'Access to 50+ bestselling audiobooks read by professional narrators. Perfect for commuting and relaxation.',
                'price': 29.99,
                'category': 'Books & Media',
                'stock': 500,
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'
            },
            
            # Fashion & Beauty
            {
                'name': 'Luxury Skincare Set',
                'description': 'Complete skincare routine with cleanser, toner, serum, and moisturizer. Natural ingredients for all skin types.',
                'price': 89.99,
                'category': 'Fashion & Beauty',
                'stock': 80,
                'image_url': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400'
            },
            {
                'name': 'Classic Denim Jacket',
                'description': 'Timeless denim jacket made from premium cotton. Perfect for casual and semi-formal occasions.',
                'price': 79.99,
                'category': 'Fashion & Beauty',
                'stock': 90,
                'image_url': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400'
            },
            
            # Sports & Fitness
            {
                'name': 'Smart Fitness Tracker',
                'description': 'Track your workouts, heart rate, sleep patterns, and daily activities. Waterproof with 7-day battery life.',
                'price': 149.99,
                'category': 'Sports & Fitness',
                'stock': 150,
                'image_url': 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400'
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Non-slip yoga mat made from eco-friendly materials. Perfect grip and cushioning for all yoga practices.',
                'price': 59.99,
                'category': 'Sports & Fitness',
                'stock': 200,
                'image_url': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400'
            },
            {
                'name': 'Adjustable Dumbbell Set',
                'description': 'Space-saving adjustable dumbbells with quick weight changes. Perfect for home workouts and strength training.',
                'price': 199.99,
                'category': 'Sports & Fitness',
                'stock': 25,
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400'
            },
            
            # Health & Wellness
            {
                'name': 'Essential Vitamins Pack',
                'description': 'Daily vitamin supplement pack with Vitamin D, B12, C, and Omega-3. Support your immune system and energy.',
                'price': 39.99,
                'category': 'Health & Wellness',
                'stock': 300,
                'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400'
            },
            {
                'name': 'Aromatherapy Diffuser Set',
                'description': 'Ultrasonic essential oil diffuser with 6 premium essential oils. Create a relaxing atmosphere at home.',
                'price': 69.99,
                'category': 'Health & Wellness',
                'stock': 100,
                'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'
            }
        ]

        for product_data in products_data:
            # Find the category
            try:
                category = Category.objects.get(name=product_data['category'])
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category {product_data["category"]} not found'))
                continue

            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'slug': slugify(product_data['name']),
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': category,
                    'stock': product_data['stock'],
                    'image_url': product_data['image_url'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')

        # Summary
        total_categories = Category.objects.count()
        total_products = Product.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\nDatabase populated successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total Categories: {total_categories}'))
        self.stdout.write(self.style.SUCCESS(f'Total Products: {total_products}'))
        self.stdout.write(self.style.SUCCESS(f'\nYou can now test the AI recommendation system by:'))
        self.stdout.write(self.style.SUCCESS(f'1. Visiting the homepage to see featured products'))
        self.stdout.write(self.style.SUCCESS(f'2. Browsing products and clicking like/dislike buttons'))
        self.stdout.write(self.style.SUCCESS(f'3. Adding items to cart and making purchases'))
        self.stdout.write(self.style.SUCCESS(f'4. Checking personalized recommendations'))