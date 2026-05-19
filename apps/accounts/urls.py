from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_view, name='auth-register'),
    path('login/', views.login_view, name='auth-login'),
    path('profile/', views.profile_view, name='auth-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]