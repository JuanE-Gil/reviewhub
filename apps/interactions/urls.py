from django.urls import path
from . import views

urlpatterns = [
    path('reviews/<int:review_id>/like/', views.toggle_like, name='toggle-like'),
    path('reviews/<int:review_id>/save/', views.toggle_save, name='toggle-save'),
    path('reviews/<int:review_id>/status/', views.review_interaction_status, name='interaction-status'),
    path('saved/', views.saved_reviews, name='saved-reviews'),
]