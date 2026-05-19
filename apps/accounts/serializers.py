from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    Incluye validación de contraseña y campo de confirmación.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'full_name', 'password', 'password_confirm')

    def validate(self, attrs):
        # validate() recibe TODOS los campos — ideal para validaciones cruzadas
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')  # esto no va al modelo
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login. No es ModelSerializer
    porque no crea ni modifica nada en la DB.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para ver y editar el perfil.
    Nunca expone la contraseña.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'bio', 'avatar', 'created_at')
        read_only_fields = ('id', 'email', 'created_at')
