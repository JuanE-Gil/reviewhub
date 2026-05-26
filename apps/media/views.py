from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import cloudinary.uploader
from drf_spectacular.utils import extend_schema

from apps.reviews.models import Review
from .models import ReviewMedia
from .serializers import ReviewMediaSerializer, ReviewMediaUploadSerializer


@extend_schema(request=ReviewMediaUploadSerializer, responses=ReviewMediaSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_media(request, review_id):
    """
    Sube una imagen o video a una reseña.
    Solo el autor de la reseña puede subir archivos.
    MultiPartParser permite recibir archivos binarios.
    """
    review = get_object_or_404(Review, pk=review_id)

    # solo el autor puede subir media
    if review.user != request.user:
        return Response(
            {'error': 'Solo el autor puede subir archivos a esta reseña.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ReviewMediaUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    file = serializer.validated_data['file']
    media_type = serializer.validated_data['media_type']
    order = serializer.validated_data.get('order', 0)

    # configuración de subida según el tipo
    upload_options = {
        'folder': f'reviewhub/reviews/{review_id}',
        'resource_type': 'auto',
    }

    # para imágenes: genera thumbnail automático
    if media_type == ReviewMedia.TYPE_IMAGE:
        upload_options['eager'] = [
            {'width': 400, 'height': 300, 'crop': 'fill', 'quality': 'auto'}
        ]

    # sube a Cloudinary
    upload_result = cloudinary.uploader.upload(file, **upload_options)

    # extrae thumbnail si existe
    thumbnail_url = ''
    if media_type == ReviewMedia.TYPE_IMAGE and upload_result.get('eager'):
        thumbnail_url = upload_result['eager'][0]['secure_url']

    # guarda el registro en DB
    media = ReviewMedia.objects.create(
        review=review,
        uploaded_by=request.user,
        media_type=media_type,
        cloudinary_url=upload_result['secure_url'],
        cloudinary_public_id=upload_result['public_id'],
        thumbnail_url=thumbnail_url,
        order=order,
    )

    return Response(
        ReviewMediaSerializer(media).data,
        status=status.HTTP_201_CREATED
    )


@extend_schema(responses=ReviewMediaSerializer(many=True))
@api_view(['GET'])
def review_media_list(request, review_id):
    """Lista todos los archivos multimedia de una reseña."""
    review = get_object_or_404(Review, pk=review_id)
    media = ReviewMedia.objects.filter(review=review)
    serializer = ReviewMediaSerializer(media, many=True)
    return Response(serializer.data)


@extend_schema(responses={204: None})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_media(request, media_id):
    """
    Elimina un archivo multimedia.
    El delete() del modelo se encarga de borrarlo en Cloudinary también.
    """
    media = get_object_or_404(ReviewMedia, pk=media_id)

    if media.uploaded_by != request.user:
        return Response(
            {'error': 'No tienes permiso para eliminar este archivo.'},
            status=status.HTTP_403_FORBIDDEN
        )

    media.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)