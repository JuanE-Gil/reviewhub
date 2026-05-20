from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Category, Review
from .serializers import (
    CategorySerializer,
    ReviewListSerializer,
    ReviewDetailSerializer,
    ReviewCreateUpdateSerializer
)


# --- Categorías --------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """Retorna solo categorías raíz con sus subcategorías anidadas."""
    categories = Category.objects.filter(
        is_active=True,
        parent=None
    ).prefetch_related('subcategories')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# --- Reseñas --------------------

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  → lista paginada de reseñas publicadas
    POST → crea una nueva reseña (requiere auth)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'category__name']
    ordering_fields = ['created_at', 'score', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Review.objects.filter(
            status=Review.STATUS_PUBLISHED
        ).select_related('user', 'category')

        # filtro opcional por categoría
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # filtro opcional por puntaje
        score = self.request.query_params.get('score')
        if score:
            queryset = queryset.filter(score=score)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateUpdateSerializer
        return ReviewListSerializer

    def perform_create(self, serializer):
        # asigna automáticamente el usuario autenticado
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → detalle completo de una reseña
    PATCH  → edita la reseña (solo el autor)
    DELETE → elimina la reseña (solo el autor)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return Review.objects.filter(
            status=Review.STATUS_PUBLISHED
        ).select_related('user', 'category').prefetch_related('rating_breakdown')

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return ReviewCreateUpdateSerializer
        return ReviewDetailSerializer

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # solo el autor puede editar o eliminar
        if request.method in ('PATCH', 'PUT', 'DELETE'):
            if obj.user != request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Solo el autor puede modificar esta reseña.')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_reviews(request):
    """Reseñas del usuario autenticado — incluye borradores."""
    reviews = Review.objects.filter(
        user=request.user
    ).select_related('category').order_by('-created_at')
    serializer = ReviewListSerializer(reviews, many=True)
    return Response(serializer.data)
