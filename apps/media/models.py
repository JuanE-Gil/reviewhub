from django.db import models
from django.contrib.auth import get_user_model
import cloudinary.uploader

User = get_user_model()

def review_media_path(instance, filename):
    """Organiza los archivos por reseña en Cloudinary"""
    return f'reviews/{instance.review.id}/{filename}'

class ReviewMedia(models.Model):

    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    ]

    review = models.ForeignKey(
        'reviews.Review',
        on_delete=models.CASCADE,
        related_name='media',
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_media',
    )

    file = models.FileField(
        upload_to=review_media_path,
        blank=True,
    )

    media_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_IMAGE,
    )

    # URL pública de Cloudinary — se guarda después de subir
    cloudinary_url = models.URLField(blank=True)
    cloudinary_public_id = models.CharField(max_length=255, blank=True)

    # para imágenes: thumbnail automático
    thumbnail_url = models.URLField(blank=True)

    # orden de aparición en la reseña
    order = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Multimedia file'
        verbose_name_plural = 'Multimedia files'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.media_type} — {self.review.title}'

    def delete(self, *args, **kwargs):
        # elimina el archivo de Cloudinary al borrar el registro
        if self.cloudinary_public_id:
            resource_type = 'video' if self.media_type == self.TYPE_VIDEO else 'image'
            cloudinary.uploader.destroy(
                self.cloudinary_public_id,
                resource_type=resource_type
            )
        super().delete(*args, **kwargs)
