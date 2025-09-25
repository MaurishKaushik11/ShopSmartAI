# Overview

This is a Django-based AI-powered e-commerce platform that combines traditional web development with machine learning capabilities. The platform features a complete online shopping experience with product catalogs, shopping cart functionality, and checkout processes. What sets it apart is its sophisticated recommendation engine that uses collaborative filtering and content-based filtering to provide personalized product suggestions to users. The recommendation system is optimized with Cython for high-performance mathematical computations, making it suitable for real-time recommendations even with large datasets.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework Architecture
The application uses Django as the primary web framework, following the Model-View-Template (MVT) pattern. The project is structured with a main `ecommerce_platform` directory containing project settings and a dedicated `ecommerce` app handling all business logic. This separation allows for modular development and easier maintenance.

## Database Design
The data model centers around core e-commerce entities: Categories, Products, Carts, CartItems, Orders, and OrderItems. Products are organized hierarchically under Categories with slug-based URLs for SEO optimization. The cart system uses session-based storage rather than user accounts, making the platform accessible to anonymous users. User interactions are tracked through a UserInteraction model that records user behavior for the recommendation engine.

## Recommendation Engine Architecture
The platform implements a hybrid recommendation system combining collaborative filtering and content-based filtering. The core machine learning computations are written in Cython (`recommendation_engine.pyx`) for performance optimization. The `RecommendationService` class manages the entire ML pipeline, including data preparation, model training, and prediction generation. The system tracks user interactions (likes, dislikes, purchases, views) to build user-item matrices for collaborative filtering.

## Performance Optimization Strategy
Critical recommendation calculations are optimized using Cython with NumPy integration. The setup.py configuration compiles Cython extensions with aggressive optimization flags (-O3, -ffast-math) to maximize computational performance. This approach allows real-time recommendation generation even with large product catalogs and user bases.

## Template and Frontend Architecture
The frontend uses Bootstrap 5 for responsive design with Font Awesome icons. The template structure follows Django best practices with a base template providing common layout and navigation. Interactive features like cart management and product interactions use AJAX for seamless user experience without page reloads.

## Session Management
The platform uses Django's session framework for cart persistence and user tracking. Each session gets a unique cart instance, and user interactions are associated with session keys. This design choice prioritizes accessibility over user registration requirements while still enabling personalized recommendations.

# External Dependencies

## Machine Learning Stack
- **scikit-learn**: Provides TF-IDF vectorization, cosine similarity calculations, and data preprocessing utilities for content-based filtering
- **NumPy**: Handles matrix operations and numerical computations within the recommendation engine
- **pandas**: Manages data manipulation and analysis for user interaction data
- **Cython**: Compiles performance-critical recommendation algorithms to C for speed optimization

## Web Development Framework
- **Django 5.2**: Core web framework providing ORM, template engine, admin interface, and URL routing
- **Bootstrap 5**: Frontend CSS framework for responsive design and UI components
- **Font Awesome**: Icon library for enhanced user interface elements

## Development and Build Tools
- **setuptools**: Manages package distribution and Cython compilation
- **django-admin**: Provides administrative interface for content management

## Database
The application is configured to work with Django's default database settings, typically SQLite for development. The ORM abstracts database operations, making it compatible with PostgreSQL, MySQL, or other Django-supported databases in production environments.

## Session and Security
Django's built-in session framework handles user state management, while CSRF protection and other security middleware provide standard web application security measures.