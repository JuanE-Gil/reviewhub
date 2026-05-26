from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.reviews.serializers import ReviewListSerializer
from .models import SearchHistory
from .services import SearchService


@api_view(['GET'])
@permission_classes([AllowAny])
def search_reviews(request):
    """
    Búsqueda principal.
    GET /api/v1/search/?q=iphone&category=tecnologia&score=4
    """
    query = request.query_params.get('q', '').strip()

    if not query:
        return Response({'error': 'The parameter q is required.'}, status=400)

    results = SearchService.search_reviews(
        query=query,
        user=request.user,
        category_slug=request.query_params.get('category'),
        score=request.query_params.get('score'),
    )

    serializer = ReviewListSerializer(results, many=True)
    return Response({
        'query': query,
        'count': len(serializer.data),
        'results': serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """
    Autocompletado en tiempo real.
    GET /api/v1/search/suggestions/?q=iph
    """
    query = request.query_params.get('q', '').strip()
    suggestions = SearchService.get_search_suggestions(query)
    return Response(suggestions)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personalized_suggestions(request):
    """
    Sugerencias personalizadas para el usuario autenticado.
    GET /api/v1/search/for-you/
    """
    suggestions = SearchService.get_suggestions_for_user(request.user)
    serializer = ReviewListSerializer(suggestions, many=True)
    return Response(serializer.data)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def search_history(request):
    """
    GET    → historial de búsquedas del usuario
    DELETE → limpia el historial
    """
    if request.method == 'DELETE':
        SearchHistory.objects.filter(user=request.user).delete()
        return Response({'message': 'Historial eliminado.'})

    history = SearchHistory.objects.filter(
        user=request.user
    ).values('query', 'result_count', 'created_at')[:20]

    return Response(list(history))