from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    """
    Categorías jerárquicas de un solo nivel.
    parent=None significa que es categoría raíz.
    Ejemplo: Tecnología > Smartphones
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Nombre del ícono, ej: fa-star'
    )
    parent = models.ForeignKey(
        'self',  # relación hacia sí mismo
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',  # category.subcategories.all()
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name

    def save(self, *args, **kwargs):
        # genera el slug automáticamente desde el nombre
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Review(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    )

    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]  # [(1,'1'), (2,'2')... (5,'5')]

    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',  # user.reviews.all()
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # PROTECT: no borra categoría si tiene reseñas
        related_name='reviews',
    )

    # Contenido
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = models.TextField()
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)

    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    # Contadores — se actualizan con signals (más adelante)
    likes_count = models.PositiveIntegerField(default=0)
    save_count = models.PositiveIntegerField(default=0)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),  # búsquedas frecuentes
            models.Index(fields=['user', 'status']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return f'{self.title} - {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # evita slugs duplicados agregando un número al final
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class RatingBreakdown(models.Model):
    """
    Criterios de evaluación individuales dentro de una reseña.
    Permite puntajes detallados por aspecto.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='rating_breakdown',
    )
    label = models.CharField(max_length=50)      # ej: "Calidad", "Precio"
    score = models.PositiveSmallIntegerField()    # 1-5

    class Meta:
        verbose_name = 'Rating Breakdown'
        verbose_name_plural = 'Rating Breakdowns'

    def __str__(self):
        return f'{self.label}: {self.score}/5'