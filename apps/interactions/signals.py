from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Like, SavedReview
from apps.reviews.models import Review
from django.db import models

def get_review_from_like(like):
    """Retorna la Review asociada a un Like, o None si no es de una Review."""
    review_ct = ContentType.objects.get_for_model(Review)
    if like.content_type == review_ct:
        return Review.objects.filter(pk=like.object_id).first()
    return None


@receiver(post_save, sender=Like)
def increment_likes_count(sender, instance, created, **kwargs):
    if created:
        review = get_review_from_like(instance)
        if review:
            Review.objects.filter(pk=review.pk).update(
                likes_count=models.F('likes_count') + 1
            )


@receiver(post_delete, sender=Like)
def decrement_likes_count(sender, instance, **kwargs):
    review = get_review_from_like(instance)
    if review:
        Review.objects.filter(pk=review.pk).update(
            likes_count=models.F('likes_count') - 1
        )


@receiver(post_save, sender=SavedReview)
def increment_saves_count(sender, instance, created, **kwargs):
    if created:
        Review.objects.filter(pk=instance.review.pk).update(
            saves_count=models.F('saves_count') + 1
        )


@receiver(post_delete, sender=SavedReview)
def decrement_saves_count(sender, instance, **kwargs):
    Review.objects.filter(pk=instance.review.pk).update(
        saves_count=models.F('saves_count') - 1
    )
