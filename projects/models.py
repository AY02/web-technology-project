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
    '''Return True if the project is public.'''
    return self.visibility == 'pub'

  def is_private(self):
    '''Return True if the project is private.'''
    return self.visibility == 'priv'

  def is_root(self):
    '''Return True if the project is a root.'''
    return self.parent is None

  def is_owner(self, user):
    '''Return True if user is the owner.'''
    return self.owner == user

  def get_user_role(self, user):
    '''
    Calculate a user's role for this project, traversing the project tree back to the
    root if necessary. Returns: 'coll', 'comm', 'view', or None.
    '''
    curr_project = self
    while curr_project is not None:
      permission = curr_project.user_permissions.filter(user=user).first()
      if permission:
        return permission.role
      curr_project = curr_project.parent
    return None
  
  def bfs(self, include_root=True):
    '''
    Performs a breadth-first search (BFS) to find all the IDs of child projects
    starting from the self parent ID. Returns a flat list of IDs (integers).
    '''
    descendants = [self.id] if include_root else []
    queue = [self.id]
    while queue:
      children = list(Project.objects.filter(parent_id__in=queue).values_list(
        'id', flat=True
      ))
      descendants.extend(children)
      queue = children
    return descendants

  def has_role(self, user):
    '''Return True if user has a role.'''
    return self.get_user_role(user) is not None
  
  def is_coll(self, user):
    'Return True if user is a collaborator.'
    return self.get_user_role(user) == 'coll'

  def can_view(self, user):
    '''Return True if user can view the project.'''
    return self.is_owner(user) or self.is_public() or self.has_role(user)
  
  def can_edit_project(self, user):
    '''Return True if user can edit the project.'''
    return self.is_owner(user) and not self.is_root()

  def can_edit_todo_document(self, user):
    '''Return True if user can edit todo entries or documents.'''
    return self.is_owner(user) or self.is_coll(user)

  def can_comment(self, user):
    '''Return True if user can comment on the project.'''
    return self.is_owner(user) or self.get_user_role(user) in ['comm', 'coll']

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
    if self.project.is_owner(self.user):
      raise ValidationError('The owner cannot have permissions on its own project.')
    if self.is_view() and self.project.is_public():
      raise ValidationError('Cannot assign the viewer role to a public project.')
    
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


class Comment(models.Model):
  # CASCADE: If we delete a project, we also delete the comments associated with it.
  project = models.ForeignKey(
    'projects.Project', 
    on_delete=models.CASCADE,
    related_name='comments'
  )
  # SET_NULL: If we delete an user, we do not delete their comments; instead, we set
  # the attribute to NULL.
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='user_comments'
  )

  title = models.CharField(max_length=128)
  content = models.TextField()

  creation_date = models.DateTimeField(auto_now_add=True)
  last_updated_date = models.DateTimeField(auto_now=True)

  class Meta:
    # By default, we sort from newest to oldest.
    ordering = ['-creation_date']

  def __str__(self):
    author = self.user.username if self.user else 'User deleted'
    return f'Comment of [{author}] {self.title[:20]} (Project: {self.project.title})'