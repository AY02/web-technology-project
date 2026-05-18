from django.db import models
from django.conf import settings


class Project(models.Model):
  # (value, label)
  VISIBILITY_CHOICES = [
    ('pub', 'Public'),
    ('priv', 'Private'),
  ]

  # The parent field is what gives projects a tree structure.
  parent = models.ForeignKey(
    'self', # A project can have another project as its parent
    on_delete=models.CASCADE, # Removing a parent node results in the recursive
                              # removal of the entire subtree rooted at that parent
                              # node.
    null=True, # If it is NULL, then it is a root project.
    blank=True, # It is not required as a field in Django forms.
    related_name='subprojects' # It renames the attribute of a parent’s children from
                               # 'project_set' to subprojects, which is semantically
                               # more appropriate
  )
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='owned_projects'
  )
  title = models.CharField(max_length=128)
  visibility = models.CharField(
    max_length=4,
    choices=VISIBILITY_CHOICES,
    default='priv' # By default, all projects are private.
  )
  # It sets the time at which the entry was created and added to the model.
  # Time format: YYYY-MM-DD HH:MM:SS
  creation_date = models.DateTimeField(auto_now_add=True)

  def get_user_role(self, user):
    """
    Calculate a user's role for this project, traversing the project tree back to the
    root if necessary. Returns: "coll", "comm", "view", or None.
    """
    curr_project = self
    while curr_project is not None:
      permission = curr_project.permissions.filter(user=user).first()
      if permission:
        return permission.role
      curr_project = curr_project.parent
    return None

  def __str__(self):
    return f"Project {self.id} (Title: {self.title}) (Owner: {self.owner.username})"


class ProjectPermission(models.Model):
  ROLE_CHOICES = [
    ("view", "Viewer"),
    ("comm", "Commentator"),
    ("coll", "Collaborator"),
  ]

  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="project_permissions"
  )
  project = models.ForeignKey(
    Project,
    on_delete=models.CASCADE,
    related_name="user_permissions"
  )
  role = models.CharField(
    max_length=4,
    choices=ROLE_CHOICES
  )
  
  class Meta:
    constraints = [
      # Uniqueness of the (user, project) pair.
      models.UniqueConstraint(
        fields=["user", "project"],
        name="unique_user_project_permission"
      )
    ]

  def __str__(self):
    # self.get_role_display(): view ==> Viewer
    return f"{self.user.username} - {self.get_role_display()} on {self.project.title}"