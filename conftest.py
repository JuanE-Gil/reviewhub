import pytest
from faker import Faker
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker('es_ES')   # datos en español peruano


@pytest.fixture
def api_client():
    """Cliente HTTP para hacer requests a la API en tests."""
    return APIClient()


@pytest.fixture
def create_user():
    """
    Factory fixture — retorna una función para crear usuarios.
    Úsalo cuando necesites crear usuarios con datos custom.
    """
    def make_user(**kwargs):
        defaults = {
            'email': fake.email(),
            'username': fake.user_name(),
            'full_name': fake.name(),
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return make_user


@pytest.fixture
def user(create_user):
    """Usuario estándar listo para usar en tests."""
    return create_user()


@pytest.fixture
def another_user(create_user):
    """Segundo usuario — para tests de permisos entre usuarios."""
    return create_user()


@pytest.fixture
def auth_client(api_client, user):
    """
    Cliente HTTP ya autenticado con JWT.
    Úsalo cuando el endpoint requiere login.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user   # referencia al usuario para los tests
    return api_client


@pytest.fixture
def category(db):
    """Categoría de prueba."""
    from apps.reviews.models import Category
    return Category.objects.create(
        name='Tecnología',
        description='Reseñas de tecnología',
    )


@pytest.fixture
def review(db, user, category):
    """Reseña publicada de prueba."""
    from apps.reviews.models import Review
    return Review.objects.create(
        user=user,
        category=category,
        title='iPhone 15 Pro Review',
        content='Contenido detallado de la reseña de prueba.',
        score=4,
        status=Review.STATUS_PUBLISHED,
    )