from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Project


# A signal is an automation mechanism that allows the programme to execute code in
# the form of a callback function when an event occurs. The signal is the event that
# occurs, whilst the receiver is the callback function that is invoked when that
# event occurs.
# Both create() and save() trigger a post_save event.


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


@receiver(post_save, sender=Project)
def propagate_visibility(sender, instance, created, **kwargs):
  """
  When a project is updated, its visibility is propagated to its subprojects.
  """

  if created:
    return
  
  def get_all_descendant_ids(project):
    ids = []
    for subproject in project.subprojects.all():
      ids.append(subproject.id)
      ids.extend(get_all_descendant_ids(subproject)) 
    return ids

  descendant_ids = get_all_descendant_ids(instance)

  if descendant_ids:
    # We use the .update() method instead of .save() because, unlike the latter, the
    # former bypasses the model and executes the update query directly on the
    # database. Consequently, it will not trigger any post_save signal, which would
    # otherwise result in redundant recursive propagation calls.
    Project.objects.filter(id__in=descendant_ids).update(visibility=instance.visibility)