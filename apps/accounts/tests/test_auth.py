import pytest
from django.urls import reverse
from rest_framework import status

# marca todos los tests de este archivo para usar la DB
pytestmark = pytest.mark.django_db


class TestUserRegistration:
    """Tests del endpoint de registro."""

    def test_register_success(self, api_client):
        """Un usuario nuevo puede registrarse con datos válidos."""
        url = reverse('auth-register')
        data = {
            'email': 'nuevo@test.com',
            'username': 'nuevousuario',
            'full_name': 'Nuevo Usuario',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert response.data['user']['email'] == 'nuevo@test.com'

    def test_register_duplicate_email(self, api_client, user):
        """No se puede registrar con un email ya existente."""
        url = reverse('auth-register')
        data = {
            'email': user.email,    # email que ya existe
            'username': 'otrousuario',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, api_client):
        """Las contraseñas deben coincidir."""
        url = reverse('auth-register')
        data = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'otrapassword',   # no coincide
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in str(response.data)


class TestUserLogin:
    """Tests del endpoint de login."""

    def test_login_success(self, api_client, user):
        """Un usuario registrado puede hacer login."""
        url = reverse('auth-login')
        data = {
            'email': user.email,
            'password': 'testpass123',
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_login_wrong_password(self, api_client, user):
        """Login con contraseña incorrecta retorna 401."""
        url = reverse('auth-login')
        data = {
            'email': user.email,
            'password': 'passwordincorrecta',
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Login con email inexistente retorna 401."""
        url = reverse('auth-login')
        data = {
            'email': 'noexiste@test.com',
            'password': 'testpass123',
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserProfile:
    """Tests del endpoint de perfil."""

    def test_get_profile_authenticated(self, auth_client):
        """Un usuario autenticado puede ver su perfil."""
        url = reverse('auth-profile')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == auth_client.user.email

    def test_get_profile_unauthenticated(self, api_client):
        """Un usuario no autenticado recibe 401."""
        url = reverse('auth-profile')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client):
        """Un usuario puede actualizar su perfil."""
        url = reverse('auth-profile')
        data = {'full_name': 'Nombre Actualizado'}
        response = auth_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Nombre Actualizado'