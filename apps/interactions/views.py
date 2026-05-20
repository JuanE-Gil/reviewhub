from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewListSerializer
from .models import Like, SavedReview


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, review_id):
    """
    Si el usuario ya dio like → lo quita.
    Si no tiene like → lo agrega.
    Patrón toggle: un endpoint hace las dos cosas.
    """
    review = get_object_or_404(Review, pk=review_id, status='published')
    content_type = ContentType.objects.get_for_model(Review)

    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=review.id,
    )

    if not created:
        # ya existía el like → eliminar
        like.delete()
        return Response({
            'liked': False,
            'likes_count': Review.objects.get(pk=review.pk).likes_count
        })

    return Response({
        'liked': True,
        'likes_count': Review.objects.get(pk=review.pk).likes_count
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_save(request, review_id):
    """Guarda o desguarda una reseña — mismo patrón toggle."""
    review = get_object_or_404(Review, pk=review_id, status='published')

    saved, created = SavedReview.objects.get_or_create(
        user=request.user,
        review=review,
    )

    if not created:
        saved.delete()
        return Response({
            'saved': False,
            'saves_count': Review.objects.get(pk=review.pk).saves_count
        })

    return Response({
        'saved': True,
        'saves_count': Review.objects.get(pk=review.pk).saves_count
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saved_reviews(request):
    """Lista de reseñas guardadas por el usuario autenticado."""
    saved = SavedReview.objects.filter(
        user=request.user
    ).select_related('review__user', 'review__category')

    reviews = [s.review for s in saved]
    serializer = ReviewListSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def review_interaction_status(request, review_id):
    """
    Retorna si el usuario autenticado dio like
    o guardó una reseña específica.
    Útil para que el frontend sepa qué íconos activar.
    """
    review = get_object_or_404(Review, pk=review_id)
    content_type = ContentType.objects.get_for_model(Review)

    liked = Like.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=review_id
    ).exists()

    saved = SavedReview.objects.filter(
        user=request.user,
        review=review
    ).exists()

    return Response({
        'liked': liked,
        'saved': saved,
        'likes_count': review.likes_count,
        'saves_count': review.saves_count,
    })