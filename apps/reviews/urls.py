from django.urls import path
from . import views

urlpatterns = [
    # Categorías
    path('categories/', views.category_list, name='categories-list'),

    # Reseñas
    path('reviews/', views.ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<slug:slug>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/me/', views.my_reviews, name='my-reviews'),
]