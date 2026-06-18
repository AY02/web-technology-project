from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Project(models.Model):
  # (value, label)
  VISIBILITY_CHOICES = [
    ("pub", "Public"),
    ("priv", "Private"),
  ]

  # The parent field is what gives projects a tree structure.
  parent = models.ForeignKey(
    "self", # A project can have another project as its parent.
    on_delete=models.CASCADE, # Removing a parent node results in the recursive
                              # removal of the entire subtree rooted at that parent
                              # node.
    null=True, # If it is NULL, then it is a root project.
    blank=True, # It is not required as a field in Django forms.
    related_name="subprojects" # It renames the attribute of a parent's children from
                               # "project_set" to subprojects, which is semantically
                               # more appropriate.
  )
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="owned_projects",
    blank=True
  )
  title = models.CharField(max_length=128)
  visibility = models.CharField(
    max_length=4,
    choices=VISIBILITY_CHOICES,
    default="priv" # By default, all projects are private.
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
      permission = curr_project.user_permissions.filter(user=user).first()
      if permission:
        return permission.role
      curr_project = curr_project.parent
    return None

  def can_user_comment_on_project(self, user):
    if self.owner == user:
      return True
    role = self.get_user_role(user)
    return role in ("comm", "coll")

  def clean(self):
    """
    A user cannot modify its own root project.
    A user can only have one root project.
    """
    super().clean()
    # Root project immutability
    if self.pk is not None:
      original = Project.objects.get(pk=self.pk)
      if original.parent is None:
        raise ValidationError("Root projects are immutable.")
    # Root project uniqueness per user
    elif self.parent is None:
      existing_root = Project.objects.filter(
        owner=self.owner,
        parent__isnull=True
      )
      if existing_root.exists():
        raise ValidationError("A user can only have one root project.")
    if self.parent and self.parent.visibility == "pub" and self.visibility == "priv":
      raise ValidationError("A public project cannot have private subprojects.")

  def save(self, *args, **kwargs):
    """
    A sub-project automatically inherits the owner from its parent.
    """
    if self.parent:
      self.owner = self.parent.owner
    self.full_clean()
    super().save(*args, **kwargs)

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
  
  def clean(self):
    """
    Extended validation logic.
    The owner cannot grant permissions to himself within its project.
    Cannot assign the 'Viewer' role to a public project.
    """
    super().clean()
    if self.project_id and self.user_id:
      if self.project.owner_id == self.user_id:
        raise ValidationError(
          "A project owner cannot have explicit permissions on its own project."
        )
      if self.role == "view" and self.project.visibility == "pub":
        raise ValidationError(
          "Cannot assign the 'Viewer' role to a public project."
        )
    
  def save(self, *args, **kwargs):
    # It forces the execution of clean() and all other validations.
    self.full_clean()
    super().save(*args, **kwargs)

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
    return f"{self.user.username} - {self.get_role_display()} on {self.project.title} (Owner: {self.project.owner.username})"


class Comment(models.Model):
  # CASCADE: If we delete a project, we also delete the comments associated with it.
  project = models.ForeignKey(
    "projects.Project", 
    on_delete=models.CASCADE,
    related_name="comments"
  )
  # SET_NULL: If we delete an user, we do not delete their comments; instead, we set
  # the attribute to NULL.
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="user_comments"
  )

  title = models.CharField(max_length=128)
  content = models.TextField()

  creation_date = models.DateTimeField(auto_now_add=True)
  last_updated_date = models.DateTimeField(auto_now=True)

  class Meta:
    # By default, we sort from newest to oldest.
    ordering = ["-creation_date"]

  def __str__(self):
    author = self.user.username if self.user else "User deleted"
    return f"Comment of [{author}] {self.title[:20]} (Project: {self.project.title})"