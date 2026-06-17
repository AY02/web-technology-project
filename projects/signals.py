from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Project, ProjectPermission


# A signal is an automation mechanism that allows the program to execute code in
# the form of a callback function when an event occurs. The signal is the event that
# occurs, whilst the receiver is the callback function that is invoked when that
# event occurs. Both create() and save() trigger a post_save event.


def bfs(parent):
  """
  Performs a breadth-first search (BFS) to find all the IDs of child projects
  starting from a parent ID. Returns a flat list of IDs (integers).
  """
  descendants = []
  queue = [parent]
  while queue:
    children = list(Project.objects.filter(parent_id__in=queue).values_list(
      "id",
      flat=True
    ))
    descendants.extend(children)
    queue = children
  return descendants


# The receiver listens for the post_save signal sent by the User model.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_root_project(sender, instance, created, **kwargs):
  """
  Automatically create a root project for every new registered user.
  """
  # The variable created is true if the user is a new entry in the User model
  # (updates do not count).
  if created:
    Project.objects.create(
      owner=instance,
      title="Root",
      parent=None # A root project has no parents.
    )


@receiver(pre_save, sender=Project)
def track_visibility_change(sender, instance, **kwargs):
  """
  Intercepts the save event before it hits the database to check if the visibility
  field has changed. If it has, we flag the instance.
  """
  if instance.pk is None:
    # It's a new project, nothing to compare against.
    instance.visibility_changed = False
    return
  original = Project.objects.get(pk=instance.pk)
  instance.visibility_changed = original.visibility != instance.visibility


@receiver(post_save, sender=Project)
def propagate_visibility(sender, instance, created, **kwargs):
  """
  When a project is updated, its visibility is propagated to its subprojects.
  Root projects are immutable, so we skip them.
  Propagation does not occurs if the visibility of the parent project remains
  unchanged.
  """
  if created or instance.parent is None or instance.visibility_changed:
    return
  descendants = bfs(instance.id)
  if descendants:
    # We use the .update() method instead of .save() because, unlike the latter, the
    # former bypasses the model and executes the update query directly on the
    # database. Consequently, it will not trigger any post_save signal, which would
    # otherwise result in redundant recursive propagation calls.
    Project.objects.filter(id__in=descendants).update(
      visibility=instance.visibility
    )


@receiver(post_save, sender=ProjectPermission)
def override_child_permissions(sender, instance, **kwargs):
  """
  If a permission is assigned to a parent project, remove any redundant permissions
  on the child projects.
  """
  descendants = bfs(instance.project_id)
  if not descendants:
    return
  ProjectPermission.objects.filter(
    project_id__in=descendants,
    user=instance.user
  ).delete()