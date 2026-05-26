from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)

User = get_user_model()


def get_tokens_for_user(user):
    """
    Genera el par de tokens JWT para un usuario.
    - refresh: larga duración, para obtener nuevos access tokens
    - access: corta duración, se manda en cada request
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@extend_schema(request=UserRegisterSerializer, responses=UserProfileSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=UserLoginSerializer, responses=UserProfileSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )

        if user is None:
            return Response(
                {'error': 'Credenciales incorrectas.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(methods=['GET'], responses=UserProfileSerializer)
@extend_schema(methods=['PATCH'], request=UserProfileSerializer, responses=UserProfileSerializer)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET  → retorna el perfil del usuario autenticado
    PATCH → actualiza parcialmente el perfil
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True  # permite enviar solo los campos que cambian
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
