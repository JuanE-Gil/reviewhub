from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


@extend_schema(responses=OpenApiResponse(description='Mapa de endpoints'))
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Mapa de endpoints disponibles en la API."""
    return Response({
        'version': 'v1',
        'docs': request.build_absolute_uri('/api/docs/'),
        'endpoints': {
            'auth': {
                'register': '/api/v1/auth/register/',
                'login': '/api/v1/auth/login/',
                'profile': '/api/v1/auth/profile/',
                'token_refresh': '/api/v1/auth/token/refresh/',
            },
            'reviews': {
                'list_create': '/api/v1/reviews/',
                'detail': '/api/v1/reviews/<slug>/',
                'my_reviews': '/api/v1/reviews/me/',
                'categories': '/api/v1/categories/',
            },
            'interactions': {
                'like': '/api/v1/interactions/reviews/<id>/like/',
                'save': '/api/v1/interactions/reviews/<id>/save/',
                'status': '/api/v1/interactions/reviews/<id>/status/',
                'saved_list': '/api/v1/interactions/saved/',
            },
            'media': {
                'upload': '/api/v1/reviews/<id>/media/upload/',
                'list': '/api/v1/reviews/<id>/media/',
                'delete': '/api/v1/media/<id>/delete/',
            },
            'search': {
                'search': '/api/v1/search/?q=<query>',
                'suggestions': '/api/v1/search/suggestions/?q=<query>',
                'for_you': '/api/v1/search/for-you/',
                'history': '/api/v1/search/history/',
            },
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.reviews.urls')),
    path('api/v1/interactions/', include('apps.interactions.urls')),
    path('api/v1/', include('apps.media.urls')),
    path('api/v1/search/', include('apps.search.urls')),
    path('api/', api_root, name='api-root'),

    # Documentación
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Sirve archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
