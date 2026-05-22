from django.urls import path
from . import views

urlpatterns = [
    path('reviews/<int:review_id>/media/', views.review_media_list, name='review-media-list'),
    path('reviews/<int:review_id>/media/upload/', views.upload_media, name='upload-media'),
    path('media/<int:media_id>/delete/', views.delete_media, name='delete-media'),
]