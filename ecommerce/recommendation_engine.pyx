# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport sqrt

# Define numpy array types for efficiency
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def compute_cosine_similarity_matrix(np.ndarray[DTYPE_t, ndim=2] matrix):
    """
    Compute cosine similarity matrix for user-item interactions
    Optimized with Cython for performance
    """
    cdef int n_users = matrix.shape[0]
    cdef int n_items = matrix.shape[1]
    cdef np.ndarray[DTYPE_t, ndim=2] similarity_matrix = np.zeros((n_users, n_users), dtype=DTYPE)
    
    cdef int i, j, k
    cdef double dot_product, norm_i, norm_j, similarity
    
    # Precompute norms for efficiency
    cdef np.ndarray[DTYPE_t, ndim=1] norms = np.zeros(n_users, dtype=DTYPE)
    for i in range(n_users):
        norm_i = 0.0
        for k in range(n_items):
            norm_i += matrix[i, k] * matrix[i, k]
        norms[i] = sqrt(norm_i)
    
    # Compute similarity matrix
    for i in range(n_users):
        for j in range(i, n_users):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                dot_product = 0.0
                for k in range(n_items):
                    dot_product += matrix[i, k] * matrix[j, k]
                
                if norms[i] > 0.0 and norms[j] > 0.0:
                    similarity = dot_product / (norms[i] * norms[j])
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
                else:
                    similarity_matrix[i, j] = 0.0
                    similarity_matrix[j, i] = 0.0
    
    return similarity_matrix

@cython.boundscheck(False)
@cython.wraparound(False)
def compute_item_similarity_matrix(np.ndarray[DTYPE_t, ndim=2] matrix):
    """
    Compute item-to-item similarity matrix
    Optimized with Cython for performance
    """
    cdef int n_users = matrix.shape[0]
    cdef int n_items = matrix.shape[1]
    cdef np.ndarray[DTYPE_t, ndim=2] item_similarity = np.zeros((n_items, n_items), dtype=DTYPE)
    
    cdef int i, j, k
    cdef double dot_product, norm_i, norm_j, similarity
    
    # Precompute item norms
    cdef np.ndarray[DTYPE_t, ndim=1] item_norms = np.zeros(n_items, dtype=DTYPE)
    for i in range(n_items):
        norm_i = 0.0
        for k in range(n_users):
            norm_i += matrix[k, i] * matrix[k, i]
        item_norms[i] = sqrt(norm_i)
    
    # Compute item similarity matrix
    for i in range(n_items):
        for j in range(i, n_items):
            if i == j:
                item_similarity[i, j] = 1.0
            else:
                dot_product = 0.0
                for k in range(n_users):
                    dot_product += matrix[k, i] * matrix[k, j]
                
                if item_norms[i] > 0.0 and item_norms[j] > 0.0:
                    similarity = dot_product / (item_norms[i] * item_norms[j])
                    item_similarity[i, j] = similarity
                    item_similarity[j, i] = similarity
                else:
                    item_similarity[i, j] = 0.0
                    item_similarity[j, i] = 0.0
    
    return item_similarity

@cython.boundscheck(False)
@cython.wraparound(False)
def fast_predict_rating(np.ndarray[DTYPE_t, ndim=2] user_item_matrix,
                       np.ndarray[DTYPE_t, ndim=2] similarity_matrix,
                       int user_idx, int item_idx, int k=10):
    """
    Fast prediction of user rating for an item using collaborative filtering
    """
    cdef int n_users = user_item_matrix.shape[0]
    cdef np.ndarray[DTYPE_t, ndim=1] similarities = similarity_matrix[user_idx, :]
    cdef np.ndarray[DTYPE_t, ndim=1] ratings = user_item_matrix[:, item_idx]
    
    # Find k most similar users who have rated this item
    cdef list similar_users = []
    cdef int i
    cdef double sim, rating
    
    for i in range(n_users):
        if i != user_idx and ratings[i] > 0:
            similar_users.append((similarities[i], i, ratings[i]))
    
    # Sort by similarity and take top k
    similar_users.sort(reverse=True)
    similar_users = similar_users[:k]
    
    if not similar_users:
        return 0.0
    
    # Compute weighted average
    cdef double weighted_sum = 0.0
    cdef double similarity_sum = 0.0
    
    for sim, user_id, rating in similar_users:
        if sim > 0:
            weighted_sum += sim * rating
            similarity_sum += abs(sim)
    
    if similarity_sum > 0:
        return weighted_sum / similarity_sum
    else:
        return 0.0

@cython.boundscheck(False) 
@cython.wraparound(False)
def compute_user_recommendations(np.ndarray[DTYPE_t, ndim=2] user_item_matrix,
                                np.ndarray[DTYPE_t, ndim=2] similarity_matrix,
                                int user_idx, int n_recommendations=5):
    """
    Compute top N recommendations for a user
    """
    cdef int n_items = user_item_matrix.shape[1]
    cdef list recommendations = []
    cdef int i
    cdef double predicted_rating
    
    for i in range(n_items):
        # Only recommend items the user hasn't interacted with
        if user_item_matrix[user_idx, i] == 0:
            predicted_rating = fast_predict_rating(user_item_matrix, similarity_matrix, user_idx, i)
            if predicted_rating > 0:
                recommendations.append((i, predicted_rating))
    
    # Sort by predicted rating and return top N
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:n_recommendations]