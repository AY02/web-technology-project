from django.contrib.auth.models import AbstractUser
from functools import wraps


def base_permission_rules(method):
  """
  Decorator for permission methods.
  1. Immediately locks out inactive users (returns False).
  2. Grants immediate access to superusers (returns True).
  3. Otherwise, executes the original method.
  """
  @wraps(method)
  def wrapper(self, *args, **kwargs):
    if not self.is_active:
      return False
    if self.is_superuser:
      return True
    return method(self, *args, **kwargs)
  return wrapper


# User includes the following fields:
# username, email, password, first_name, last_name
# Note: While the username is unique, the email is not.
class User(AbstractUser):

  def is_owner_of(self, project):
    return self == project.owner
  
  def get_role_in(self, project):
    """
    Calculates the user's role for a given project, traversing the project tree back
    to the root if necessary.
    Returns: 'view', 'comm', 'coll', or None.
    """
    current_project = project
    while current_project is not None:
      permission = current_project.user_permissions.filter(user=self).first()
      if permission:
        return permission.role
      current_project = current_project.parent
    return None
  
  def is_view_of(self, project):
    return self.get_role_in(project) == 'view'
  
  def is_comm_of(self, project):
    return self.get_role_in(project) == 'comm'
  
  def is_coll_of(self, project):
    return self.get_role_in(project) == 'coll'
  
  def has_role_in(self, project):
    return self.get_role_in(project) is not None
  
  @base_permission_rules
  def can_view(self, project):
    """
    The user can view a project if and only if he has a role, or is the owner, or
    it is a public project.
    """
    return (
      self.has_role_in(project) or
      self.is_owner_of(project) or
      project.is_public()
    )
  
  @base_permission_rules
  def can_comment_on(self, project):
    """
    The user can comment on a project if and only if he is a commentator, a
    collaborator, or the owner.
    """
    return (
      self.is_comm_of(project) or
      self.is_coll_of(project) or
      self.is_owner_of(project)
    )

  @base_permission_rules
  def can_edit_project(self, project):
    """
    The user can modify a project if and only if he is the owner and the project is
    not the root project.
    """
    return self.is_owner_of(project) and not project.is_root()
  
  @base_permission_rules
  def can_edit_todolist(self, todolist):
    """
    The user can edit a todolist if and only if he is a collaborator of the parent
    project, or is its owner.
    """
    return (
      self.is_coll_of(todolist.project_parent) or
      self.is_owner_of(todolist.project_parent)
    )
  
  @base_permission_rules
  def can_edit_document(self, document):
    """
    The user can edit a document if and only if he is a collaborator of the parent
    project, or is its owner.
    """
    return (
      self.is_coll_of(document.project_parent) or
      self.is_owner_of(document.project_parent)
    )