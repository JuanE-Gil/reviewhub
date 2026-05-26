from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SearchHistory(models.Model):
    """
    Registra las búsquedas del usuario.
    Sirve para mostrar búsquedas recientes y
    calcular sus intereses por términos.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    query = models.CharField(max_length=200)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering = ['-created_at']
        # máximo 1 registro por query por usuario — evita duplicados
        unique_together = ('user', 'query')

    def __str__(self):
        return f'{self.user.username} buscó: {self.query}'


class ReviewView(models.Model):
    """
    Registra qué reseñas vio cada usuario.
    Es la base del algoritmo de sugerencias —
    si alguien ve reseñas de Tecnología, le sugerimos más.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_views'
    )
    review = models.ForeignKey(
        'reviews.Review',
        on_delete=models.CASCADE,
        related_name='views'
    )
    view_count = models.PositiveIntegerField(default=1)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vista de reseña'
        verbose_name_plural = 'Vistas de reseñas'
        unique_together = ('user', 'review')
        ordering = ['-last_viewed']

    def __str__(self):
        return f'{self.user.username} vio: {self.review.title}'
