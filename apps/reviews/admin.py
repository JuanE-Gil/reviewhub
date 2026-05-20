from django.contrib import admin
from .models import Category, Review, RatingBreakdown

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # genera slug en tiempo real
    fields = ('name', 'slug', 'description', 'icon', 'parent', 'is_active')

class RatingBreakdownInline(admin.TabularInline):
    """
    Permite editar los criterios de rating
    directamente desde la reseña en el admin.
    """
    model = RatingBreakdown
    extra = 3
    max_num = 10

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'score', 'status', 'created_at')
    list_filter = ('status', 'score', 'category')
    search_fields = ('title', 'content', 'user__email')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('user',)       # evita cargar todos los usuarios en un select
    inlines = [RatingBreakdownInline]

    # acción personalizada en el admin
    actions = ['publish_reviews']

    def publish_reviews(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} published review(s)')
    publish_reviews.short_description = 'Publish selected reviews'