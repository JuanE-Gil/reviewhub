from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)
from django.db.models import Count, Q
from apps.reviews.models import Review, Category
from .models import SearchHistory, ReviewView


class SearchService:
    """
    Servicio de búsqueda con PostgreSQL Full-Text Search.
    Separar la lógica en un Service hace las views más limpias
    y la lógica más fácil de testear.
    """

    @staticmethod
    def search_reviews(query, user=None, category_slug=None, score=None):
        """
        Búsqueda full-text en título y contenido.
        Rankea por relevancia — los resultados más relevantes primero.
        """
        # SearchVector define qué campos buscar y su peso
        # 'A' es mayor peso que 'B' — el título importa más que el contenido
        vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
        search_query = SearchQuery(query, config='spanish')

        results = Review.objects.filter(
            status=Review.STATUS_PUBLISHED
        ).annotate(
            rank=SearchRank(vector, search_query)
        ).filter(
            # filtra resultados con algo de relevancia
            Q(rank__gte=0.01) |
            Q(title__icontains=query)   # fallback: búsqueda simple
        ).select_related('user', 'category').order_by('-rank')

        # filtros opcionales
        if category_slug:
            results = results.filter(category__slug=category_slug)
        if score:
            results = results.filter(score=score)

        # guarda en historial si hay usuario autenticado
        if user and user.is_authenticated and query.strip():
            SearchHistory.objects.update_or_create(
                user=user,
                query=query.lower().strip(),
                defaults={'result_count': results.count()}
            )

        return results

    @staticmethod
    def get_suggestions_for_user(user, limit=10):
        """
        Sugerencias personalizadas basadas en:
        1. Categorías de reseñas que el usuario vio
        2. Categorías de reseñas que el usuario likeó
        3. Excluyendo reseñas que ya vio
        """
        if not user.is_authenticated:
            # para usuarios anónimos: las más populares
            return Review.objects.filter(
                status=Review.STATUS_PUBLISHED
            ).order_by('-likes_count')[:limit]

        # categorías que más le interesan al usuario
        viewed_categories = ReviewView.objects.filter(
            user=user
        ).values('review__category').annotate(
            total=Count('review__category')
        ).order_by('-total').values_list('review__category', flat=True)[:5]

        # reseñas ya vistas — para excluirlas
        viewed_review_ids = ReviewView.objects.filter(
            user=user
        ).values_list('review_id', flat=True)

        if viewed_categories:
            # sugerencias basadas en intereses
            suggestions = Review.objects.filter(
                status=Review.STATUS_PUBLISHED,
                category__in=viewed_categories,
            ).exclude(
                id__in=viewed_review_ids
            ).exclude(
                user=user   # no sugerir las propias reseñas
            ).select_related('user', 'category').order_by('-likes_count', '-created_at')
        else:
            # usuario nuevo sin historial: las más populares
            suggestions = Review.objects.filter(
                status=Review.STATUS_PUBLISHED
            ).exclude(
                user=user
            ).select_related('user', 'category').order_by('-likes_count', '-created_at')

        return suggestions[:limit]

    @staticmethod
    def get_search_suggestions(query, limit=5):
        """
        Autocompletado — sugiere títulos mientras el usuario escribe.
        Se llama con cada keystroke desde el frontend.
        """
        if len(query) < 2:
            return []

        titles = Review.objects.filter(
            status=Review.STATUS_PUBLISHED,
            title__icontains=query
        ).values_list('title', flat=True)[:limit]

        categories = Category.objects.filter(
            is_active=True,
            name__icontains=query
        ).values_list('name', flat=True)[:3]

        return {
            'reviews': list(titles),
            'categories': list(categories),
        }

    @staticmethod
    def register_view(user, review):
        """
        Registra que un usuario vio una reseña.
        Si ya la vio antes, incrementa el contador.
        """
        if not user.is_authenticated:
            return

        obj, created = ReviewView.objects.get_or_create(
            user=user,
            review=review,
        )
        if not created:
            ReviewView.objects.filter(pk=obj.pk).update(
                view_count=obj.view_count + 1
            )