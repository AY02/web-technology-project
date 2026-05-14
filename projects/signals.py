from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Project

# The receiver listens for the post_save signal sent by the User model.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_root_project(sender, instance, created, **kwargs):
  """
  Automatically create a root project for every new registered user.
  """
  # created is true if the user is a new entry in the User model (updates do not
  # count).
  if created:
    Project.objects.create(
      owner=instance,
      title='Root',
      parent=None, # A root project has no parents.
      visibility='priv' # By default, the root project is private.
    )