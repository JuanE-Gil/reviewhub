from rest_framework import serializers
from .models import Category, Review, RatingBreakdown
from apps.accounts.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'icon', 'parent', 'subcategories')

    @staticmethod
    def get_subcategories(obj):
        # solo retorna subcategorías si es categoría raíz
        if obj.parent is None:
            return CategorySerializer(
                obj.subcategories.filter(is_active=True),
                many=True
            ).data
        return []


class RatingBreakdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingBreakdown
        fields = ('id', 'label', 'score')


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listas — solo campos esenciales.
    Úsalo cuando retornes muchas reseñas a la vez.
    """
    user = UserProfileSerializer()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'title', 'slug', 'score',
            'user', 'category_name',
            'likes_count', 'saves_count', 'created_at'
        )


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para ver una reseña individual.
    Incluye el desglose de rating y datos completos.
    """
    user = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    rating_breakdown = RatingBreakdownSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'title', 'slug', 'content', 'score',
            'user', 'category', 'rating_breakdown',
            'status', 'likes_count',
            'created_at', 'updated_at'
        )


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y editar reseñas.
    Maneja el rating_breakdown como escritura anidada.
    """
    rating_breakdown = RatingBreakdownSerializer(many=True, required=False)

    class Meta:
        model = Review
        fields = (
            'title', 'content', 'score',
            'category', 'status', 'rating_breakdown'
        )

    @staticmethod
    def validate_score(value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('El puntaje debe estar entre 1 y 5.')
        return value

    @staticmethod
    def validate_rating_breakdown(value):
        for item in value:
            if not 1 <= item['score'] <= 5:
                raise serializers.ValidationError(
                    f'El puntaje de "{item["label"]}" debe estar entre 1 y 5.'
                )
        return value

    def create(self, validated_data):
        # extraemos el breakdown antes de crear la reseña
        breakdown_data = validated_data.pop('rating_breakdown', [])
        review = Review.objects.create(**validated_data)

        # creamos cada criterio asociado a la reseña
        for item in breakdown_data:
            RatingBreakdown.objects.create(review=review, **item)

        return review

    def update(self, instance, validated_data):
        breakdown_data = validated_data.pop('rating_breakdown', None)

        # actualiza los campos de la reseña
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # si vienen nuevos criterios, reemplaza los anteriores
        if breakdown_data is not None:
            instance.rating_breakdown.all().delete()
            for item in breakdown_data:
                RatingBreakdown.objects.create(review=instance, **item)

        return instance
