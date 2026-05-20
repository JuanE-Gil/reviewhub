from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Like(models.Model):
    """
    Like genérico — funciona para cualquier modelo.
    La combinación user + content_type + object_id es única,
    así un usuario no puede dar like dos veces al mismo objeto.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        # constraint: un like por usuario por objeto
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'{self.user.username} → {self.content_object}'

class SavedReview(models.Model):
    """
    Reseñas guardadas por un usuario.
    A diferencia de Like, este es específico para reseñas
    porque en el futuro tendrá colecciones y notas privadas.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_reviews'
    )
    review = models.ForeignKey(
        'reviews.Review',
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Saved review'
        verbose_name_plural = 'Saved reviews'
        unique_together = ('user', 'review')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} guardó → {self.review.title}'