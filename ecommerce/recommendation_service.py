import numpy as np
import pandas as pd
from django.db import models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import logging

from .models import Product, UserInteraction, Cart, CartItem
from .recommendation_engine import (
    compute_cosine_similarity_matrix,
    compute_item_similarity_matrix,
    compute_user_recommendations,
    fast_predict_rating
)

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Machine Learning recommendation service using collaborative filtering
    with Cython-optimized calculations for performance
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_mapping = {}
        self.item_mapping = {}
        self.reverse_user_mapping = {}
        self.reverse_item_mapping = {}
        self.content_features = None
        self.is_trained = False
    
    def prepare_interaction_data(self):
        """
        Prepare user-item interaction data from the database
        """
        try:
            # Get all interactions with weights
            interactions = UserInteraction.objects.all()
            
            if not interactions.exists():
                logger.warning("No user interactions found")
                return None
            
            # Create interaction matrix with weighted scores
            interaction_data = []
            for interaction in interactions:
                weight = self._get_interaction_weight(interaction.interaction_type)
                interaction_data.append({
                    'session_key': interaction.session_key,
                    'product_id': interaction.product.id,
                    'weight': weight,
                    'timestamp': interaction.timestamp
                })
            
            if not interaction_data:
                return None
            
            df = pd.DataFrame(interaction_data)
            
            # Group by session_key and product_id to aggregate weights
            user_item_df = df.groupby(['session_key', 'product_id'])['weight'].sum().reset_index()
            
            # Create mappings
            unique_users = user_item_df['session_key'].unique()
            unique_items = user_item_df['product_id'].unique()
            
            self.user_mapping = {user: idx for idx, user in enumerate(unique_users)}
            self.item_mapping = {item: idx for idx, item in enumerate(unique_items)}
            self.reverse_user_mapping = {idx: user for user, idx in self.user_mapping.items()}
            self.reverse_item_mapping = {idx: item for item, idx in self.item_mapping.items()}
            
            # Create user-item matrix
            n_users = len(unique_users)
            n_items = len(unique_items)
            
            user_item_matrix = np.zeros((n_users, n_items), dtype=np.float64)
            
            for _, row in user_item_df.iterrows():
                user_idx = self.user_mapping[row['session_key']]
                item_idx = self.item_mapping[row['product_id']]
                user_item_matrix[user_idx, item_idx] = row['weight']
            
            return user_item_matrix
            
        except Exception as e:
            logger.error(f"Error preparing interaction data: {str(e)}")
            return None
    
    def _get_interaction_weight(self, interaction_type):
        """
        Assign weights to different interaction types
        """
        weights = {
            'view': 1.0,
            'like': 3.0,
            'dislike': -2.0,
            'purchase': 5.0
        }
        return weights.get(interaction_type, 1.0)
    
    def prepare_content_features(self):
        """
        Prepare content-based features for products
        """
        try:
            products = Product.objects.filter(is_active=True)
            
            if not products.exists():
                return None
            
            # Create content features from product descriptions
            descriptions = [f"{p.name} {p.description} {p.category.name}" for p in products]
            
            # Use TF-IDF for text features
            tfidf = TfidfVectorizer(max_features=100, stop_words='english')
            content_matrix = tfidf.fit_transform(descriptions).toarray()
            
            # Normalize price features
            prices = np.array([float(p.price) for p in products]).reshape(-1, 1)
            scaler = StandardScaler()
            normalized_prices = scaler.fit_transform(prices)
            
            # Combine features
            content_features = np.hstack([content_matrix, normalized_prices])
            
            return content_features
            
        except Exception as e:
            logger.error(f"Error preparing content features: {str(e)}")
            return None
    
    def train_model(self):
        """
        Train the recommendation model using collaborative filtering
        """
        try:
            logger.info("Training recommendation model...")
            
            # Prepare interaction data
            self.user_item_matrix = self.prepare_interaction_data()
            
            if self.user_item_matrix is None:
                logger.warning("No interaction data available for training")
                return False
            
            # Compute similarity matrices using Cython-optimized functions
            logger.info("Computing user similarity matrix...")
            self.user_similarity_matrix = compute_cosine_similarity_matrix(self.user_item_matrix)
            
            logger.info("Computing item similarity matrix...")
            self.item_similarity_matrix = compute_item_similarity_matrix(self.user_item_matrix)
            
            # Prepare content features
            self.content_features = self.prepare_content_features()
            
            self.is_trained = True
            logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def get_user_recommendations(self, session_key, n_recommendations=5):
        """
        Get personalized recommendations for a user
        """
        try:
            if not self.is_trained:
                self.train_model()
            
            if not self.is_trained or session_key not in self.user_mapping:
                # Fallback to popular items for new users
                return self._get_popular_recommendations(n_recommendations)
            
            user_idx = self.user_mapping[session_key]
            
            # Get recommendations using Cython-optimized function
            recommendations = compute_user_recommendations(
                self.user_item_matrix,
                self.user_similarity_matrix,
                user_idx,
                n_recommendations
            )
            
            # Convert item indices back to product IDs
            product_recommendations = []
            for item_idx, score in recommendations:
                product_id = self.reverse_item_mapping[item_idx]
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                    product_recommendations.append({
                        'product': product,
                        'score': score,
                        'reason': 'collaborative_filtering'
                    })
                except Product.DoesNotExist:
                    continue
            
            return product_recommendations
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {str(e)}")
            return self._get_popular_recommendations(n_recommendations)
    
    def get_similar_products(self, product_id, n_recommendations=5):
        """
        Get products similar to a given product
        """
        try:
            if not self.is_trained:
                self.train_model()
            
            if not self.is_trained or product_id not in self.item_mapping:
                return self._get_category_recommendations(product_id, n_recommendations)
            
            item_idx = self.item_mapping[product_id]
            
            # Get item similarities
            similarities = self.item_similarity_matrix[item_idx, :]
            
            # Get top similar items
            similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]  # Exclude self
            
            similar_products = []
            for idx in similar_indices:
                if similarities[idx] > 0:
                    similar_product_id = self.reverse_item_mapping[idx]
                    try:
                        product = Product.objects.get(id=similar_product_id, is_active=True)
                        similar_products.append({
                            'product': product,
                            'score': similarities[idx],
                            'reason': 'item_similarity'
                        })
                    except Product.DoesNotExist:
                        continue
            
            return similar_products
            
        except Exception as e:
            logger.error(f"Error getting similar products: {str(e)}")
            return self._get_category_recommendations(product_id, n_recommendations)
    
    def _get_popular_recommendations(self, n_recommendations=5):
        """
        Fallback recommendations based on popularity
        """
        try:
            # Get products with most positive interactions
            popular_products = Product.objects.filter(
                is_active=True
            ).annotate(
                interaction_count=models.Count('userinteraction')
            ).order_by('-interaction_count')[:n_recommendations]
            
            return [{'product': p, 'score': 1.0, 'reason': 'popularity'} 
                   for p in popular_products]
                   
        except Exception as e:
            logger.error(f"Error getting popular recommendations: {str(e)}")
            return []
    
    def _get_category_recommendations(self, product_id, n_recommendations=5):
        """
        Fallback recommendations based on product category
        """
        try:
            product = Product.objects.get(id=product_id)
            similar_products = Product.objects.filter(
                category=product.category,
                is_active=True
            ).exclude(id=product_id)[:n_recommendations]
            
            return [{'product': p, 'score': 1.0, 'reason': 'same_category'} 
                   for p in similar_products]
                   
        except (Product.DoesNotExist, Exception) as e:
            logger.error(f"Error getting category recommendations: {str(e)}")
            return []
    
    def record_interaction(self, session_key, product_id, interaction_type):
        """
        Record a user interaction and update recommendations
        """
        try:
            product = Product.objects.get(id=product_id)
            
            # Create or update interaction
            interaction, created = UserInteraction.objects.get_or_create(
                session_key=session_key,
                product=product,
                interaction_type=interaction_type,
                defaults={'timestamp': models.timezone.now()}
            )
            
            if not created:
                interaction.timestamp = models.timezone.now()
                interaction.save()
            
            # Retrain model periodically (every 50 interactions)
            interaction_count = UserInteraction.objects.count()
            if interaction_count % 50 == 0:
                self.train_model()
            
            return True
            
        except Product.DoesNotExist:
            logger.error(f"Product with id {product_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error recording interaction: {str(e)}")
            return False

# Global instance
recommendation_service = RecommendationService()