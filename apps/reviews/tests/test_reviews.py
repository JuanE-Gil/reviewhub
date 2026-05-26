import pytest
from django.urls import reverse
from rest_framework import status
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


class TestReviewList:
    """Tests del listado de reseñas."""

    def test_list_published_reviews(self, api_client, review):
        """Cualquier usuario puede ver reseñas publicadas."""
        url = reverse('review-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_draft_reviews_not_visible(self, api_client, user, category):
        """Los borradores no aparecen en el listado público."""
        Review.objects.create(
            user=user,
            category=category,
            title='Borrador',
            content='Contenido borrador',
            score=3,
            status=Review.STATUS_DRAFT,
        )
        url = reverse('review-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_filter_by_category(self, api_client, review, category):
        """Se puede filtrar reseñas por categoría."""
        url = reverse('review-list-create')
        response = api_client.get(url, {'category': category.slug})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


class TestReviewCreate:
    """Tests de creación de reseñas."""

    def test_create_review_authenticated(self, auth_client, category):
        """Un usuario autenticado puede crear una reseña."""
        url = reverse('review-list-create')
        data = {
            'title': 'Nueva Reseña de Prueba',
            'content': 'Contenido de la reseña con suficiente detalle.',
            'score': 5,
            'category': category.id,
            'status': 'published',
        }
        response = auth_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_review_unauthenticated(self, api_client, category):
        """Un usuario no autenticado no puede crear reseñas."""
        url = reverse('review-list-create')
        data = {
            'title': 'Reseña sin auth',
            'content': 'Contenido',
            'score': 3,
            'category': category.id,
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_review_invalid_score(self, auth_client, category):
        """El puntaje debe estar entre 1 y 5."""
        url = reverse('review-list-create')
        data = {
            'title': 'Reseña score inválido',
            'content': 'Contenido',
            'score': 10,    # inválido
            'category': category.id,
        }
        response = auth_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestReviewPermissions:
    """Tests de permisos entre usuarios."""

    def test_user_cannot_delete_others_review(
        self, api_client, another_user, review
    ):
        """Un usuario no puede eliminar la reseña de otro."""
        from rest_framework_simplejwt.tokens import RefreshToken
        # autenticamos como otro usuario
        refresh = RefreshToken.for_user(another_user)
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

        url = reverse('review-detail', kwargs={'slug': review.slug})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Review.objects.filter(pk=review.pk).exists()

    def test_author_can_delete_own_review(self, auth_client, review):
        """El autor sí puede eliminar su propia reseña."""
        url = reverse('review-detail', kwargs={'slug': review.slug})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(pk=review.pk).exists()