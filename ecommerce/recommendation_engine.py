import numpy as np

def compute_cosine_similarity_matrix(matrix):
    """
    Compute cosine similarity matrix for user-item interactions
    Pure Python implementation
    """
    n_users = matrix.shape[0]
    similarity_matrix = np.zeros((n_users, n_users), dtype=np.float64)
    
    # Precompute norms for efficiency
    norms = np.zeros(n_users, dtype=np.float64)
    for i in range(n_users):
        norms[i] = np.sqrt(np.sum(matrix[i, :] ** 2))
    
    # Compute similarity matrix
    for i in range(n_users):
        for j in range(i, n_users):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                dot_product = np.dot(matrix[i, :], matrix[j, :])
                if norms[i] > 0.0 and norms[j] > 0.0:
                    similarity = dot_product / (norms[i] * norms[j])
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
                else:
                    similarity_matrix[i, j] = 0.0
                    similarity_matrix[j, i] = 0.0
    
    return similarity_matrix

def compute_item_similarity_matrix(matrix):
    """
    Compute item-to-item similarity matrix
    Pure Python implementation
    """
    n_users, n_items = matrix.shape
    item_similarity = np.zeros((n_items, n_items), dtype=np.float64)
    
    # Precompute item norms
    item_norms = np.zeros(n_items, dtype=np.float64)
    for i in range(n_items):
        item_norms[i] = np.sqrt(np.sum(matrix[:, i] ** 2))
    
    # Compute item similarity matrix
    for i in range(n_items):
        for j in range(i, n_items):
            if i == j:
                item_similarity[i, j] = 1.0
            else:
                dot_product = np.dot(matrix[:, i], matrix[:, j])
                if item_norms[i] > 0.0 and item_norms[j] > 0.0:
                    similarity = dot_product / (item_norms[i] * item_norms[j])
                    item_similarity[i, j] = similarity
                    item_similarity[j, i] = similarity
                else:
                    item_similarity[i, j] = 0.0
                    item_similarity[j, i] = 0.0
    
    return item_similarity

def fast_predict_rating(user_item_matrix, similarity_matrix, user_idx, item_idx, k=10):
    """
    Fast prediction of user rating for an item using collaborative filtering
    Pure Python implementation
    """
    similarities = similarity_matrix[user_idx, :]
    ratings = user_item_matrix[:, item_idx]
    
    # Find k most similar users who have rated this item
    similar_users = []
    for i in range(len(similarities)):
        if i != user_idx and ratings[i] > 0:
            similar_users.append((similarities[i], i, ratings[i]))
    
    # Sort by similarity and take top k
    similar_users.sort(reverse=True)
    similar_users = similar_users[:k]
    
    if not similar_users:
        return 0.0
    
    # Compute weighted average
    weighted_sum = 0.0
    similarity_sum = 0.0
    
    for sim, user_id, rating in similar_users:
        if sim > 0:
            weighted_sum += sim * rating
            similarity_sum += abs(sim)
    
    if similarity_sum > 0:
        return weighted_sum / similarity_sum
    else:
        return 0.0

def compute_user_recommendations(user_item_matrix, similarity_matrix, user_idx, n_recommendations=5):
    """
    Compute top N recommendations for a user
    Pure Python implementation
    """
    n_items = user_item_matrix.shape[1]
    recommendations = []
    
    for i in range(n_items):
        # Only recommend items the user hasn't interacted with
        if user_item_matrix[user_idx, i] == 0:
            predicted_rating = fast_predict_rating(user_item_matrix, similarity_matrix, user_idx, i)
            if predicted_rating > 0:
                recommendations.append((i, predicted_rating))
    
    # Sort by predicted rating and return top N
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:n_recommendations]