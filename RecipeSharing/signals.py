from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from notifications.signals import notify
from .models import Recipe, Comment
from django.contrib.auth.models import User

@receiver(m2m_changed, sender=Recipe.liked_by.through)
def notify_on_like(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            user = User.objects.get(pk=pk)
            if user != instance.author:
                notify.send(
                    sender=user,
                    recipient=instance.author,
                    verb="liked your recipe",
                    target=instance,
                    action_object=instance,
                    description=f"{user.username} liked your recipe '{instance.title}'",
                )

@receiver(m2m_changed, sender=Recipe.saved_by.through)
def notify_on_save(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            user = User.objects.get(pk=pk)
            if user != instance.author:
                notify.send(
                    sender=user,
                    recipient=instance.author,
                    verb="saved your recipe",
                    target=instance,
                    action_object=instance,
                    description=f"{user.username} saved your recipe '{instance.title}'",
                )

@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if created and instance.author != instance.recipe.author:
        notify.send(
            sender=instance.author,
            recipient=instance.recipe.author,
            verb="commented on your recipe",
            target=instance.recipe,
            action_object=instance,
            description=f"{instance.author.username} commented on your recipe '{instance.recipe.title}'",
        )