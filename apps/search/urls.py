from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_reviews, name='search'),
    path('suggestions/', views.search_suggestions, name='search-suggestions'),
    path('for-you/', views.personalized_suggestions, name='for-you'),
    path('history/', views.search_history, name='search-history'),
]