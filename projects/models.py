from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Project(models.Model):
  # (value, label)
  VISIBILITY_CHOICES = [
    ('pub', 'Public'),
    ('priv', 'Private'),
  ]

  # The parent field is what gives projects a tree structure.
  parent = models.ForeignKey(
    'self', # A project can have another project as its parent.
    on_delete=models.CASCADE, # Removing a parent node results in the recursive
                              # removal of the entire subtree rooted at that parent
                              # node.
    null=True, # If it is NULL, then it is a root project.
    blank=True, # It is not required as a field in Django forms.
    related_name='subprojects' # It renames the attribute of a parent's children from
                               # 'project_set' to subprojects, which is semantically
                               # more appropriate.
  )
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='owned_projects',
    blank=True
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

  def is_public(self):
    return self.visibility == 'pub'

  def is_private(self):
    return self.visibility == 'priv'

  def is_root(self):
    '''Return True if the project is a root.'''
    return self.parent is None

  def is_owner(self, user):
    return self.owner == user
  
  def get_permissions(self):
    """
    Returns a list containing the effective permissions for this project, including
    those inherited from parent projects.
    """
    permissions = {}
    current_project = self
    while current_project is not None:
      for perm in current_project.user_permissions.select_related('user', 'project'):
        if perm.user not in permissions:
          permissions[perm.user] = perm
      current_project = current_project.parent
    return list(permissions.values())
  
  def bfs(self, include_root=True):
    """
    Performs a breadth-first search (BFS) to find all the IDs of child projects
    starting from the self parent ID. Returns a flat list of IDs (integers).
    """
    descendants = [self.id] if include_root else []
    queue = [self.id]
    while queue:
      children = list(Project.objects.filter(parent_id__in=queue).values_list(
        'id',
        flat=True
      ))
      descendants.extend(children)
      queue = children
    return descendants

  def clean(self):
    super().clean()
    if self.id is not None and self.is_root():
      raise ValidationError('Root projects are immutable.')
    if not self.is_root() and self.parent.is_public() and self.is_private():
      raise ValidationError('A public project cannot have private subprojects.')

  def save(self, *args, **kwargs):
    '''A subproject automatically inherits the owner from its parent.'''
    if not self.is_root():
      self.owner = self.parent.owner
    self.full_clean()
    super().save(*args, **kwargs)
  
  def delete(self, *args, **kwargs):
    if self.is_root():
      raise ValidationError("You can't delete a root project manually. Remove the owner if necessary.")
    super().delete(*args, **kwargs)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['owner'],
        condition=models.Q(parent__isnull=True),
        name='unique_root_project_per_user',
        violation_error_message='A user has one and only one root project.'
      )
    ]
  
  def __str__(self):
    return f'Project {self.id} (Title: {self.title}) (Owner: {self.owner.username})'


class ProjectPermission(models.Model):
  ROLE_CHOICES = [
    ('view', 'Viewer'),
    ('comm', 'Commentator'),
    ('coll', 'Collaborator'),
  ]

  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='project_permissions'
  )
  project = models.ForeignKey(
    Project,
    on_delete=models.CASCADE,
    related_name='user_permissions'
  )
  role = models.CharField(
    max_length=4,
    choices=ROLE_CHOICES
  )
  
  def is_view(self):
    return self.role == 'view'
  
  def is_comm(self):
    return self.role == 'comm'
  
  def is_coll(self):
    return self.role == 'coll'

  def clean(self):
    super().clean()
    if self.user.is_owner_of(self.project):
      raise ValidationError('The owner cannot have permissions on its own project.')
    if self.is_view() and self.project.is_public():
      raise ValidationError('Cannot assign the viewer role to a public project.')
    current_parent = self.project.parent
    while current_parent is not None:
      ancestor_permission = ProjectPermission.objects.filter(
        project=current_parent, 
        user=self.user
      ).first()
      if not ancestor_permission:
        current_parent = current_parent.parent
        continue
      raise ValidationError(
        f"Unable to assign a role on '{self.project.title}'. "
        f"The user already inherits the role of '{ancestor_permission.get_role_display()}' "
        f"from the parent project '{current_parent.title}'."
      )
    
  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['user', 'project'],
        name='unique_user_project_permission',
        violation_error_message = 'A user can have at most only one permission on the same project.'
      )
    ]

  def __str__(self):
    # self.get_role_display(): view ==> Viewer
    return f'{self.user.username} - {self.get_role_display()} on {self.project.title} (Owner: {self.project.owner.username})'