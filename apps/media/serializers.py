from rest_framework import serializers
from .models import ReviewMedia


ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/avi']
MAX_IMAGE_SIZE = 5 * 1024 * 1024    # 5 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


class ReviewMediaSerializer(serializers.ModelSerializer):
    """Serializer para mostrar media de una reseña."""

    class Meta:
        model = ReviewMedia
        fields = (
            'id', 'media_type', 'cloudinary_url',
            'thumbnail_url', 'order', 'created_at'
        )
        read_only_fields = fields


class ReviewMediaUploadSerializer(serializers.Serializer):
    """
    Serializer para subir archivos.
    No es ModelSerializer porque manejamos
    la subida manualmente a Cloudinary.
    """
    file = serializers.FileField()
    media_type = serializers.ChoiceField(
        choices=[ReviewMedia.TYPE_IMAGE, ReviewMedia.TYPE_VIDEO]
    )
    order = serializers.IntegerField(default=0, required=False)

    def validate(self, attrs):
        file = attrs['file']
        media_type = attrs['media_type']

        # usamos el nombre del archivo como fallback más confiable
        filename = file.name.lower()
        content_type = getattr(file, 'content_type', '')

        if media_type == ReviewMedia.TYPE_IMAGE:
            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            valid_types = ALLOWED_IMAGE_TYPES + ['application/octet-stream', '']

            if not filename.endswith(valid_extensions) and content_type not in valid_types:
                raise serializers.ValidationError(
                    'Formato de imagen no permitido. Usa JPG, PNG o WebP.'
                )
            if file.size > MAX_IMAGE_SIZE:
                raise serializers.ValidationError('La imagen no puede superar 5MB.')

        elif media_type == ReviewMedia.TYPE_VIDEO:
            valid_extensions = ('.mp4', '.mov', '.avi')
            valid_types = ALLOWED_VIDEO_TYPES + ['application/octet-stream', '']

            if not filename.endswith(valid_extensions) and content_type not in valid_types:
                raise serializers.ValidationError(
                    'Formato de video no permitido. Usa MP4, MOV o AVI.'
                )
            if file.size > MAX_VIDEO_SIZE:
                raise serializers.ValidationError('El video no puede superar 100MB.')

        return attrs