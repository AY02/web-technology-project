from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Document(models.Model):
  project_parent = models.ForeignKey(
    'projects.Project',
    on_delete=models.CASCADE,
    related_name='documents'
  )
  title = models.CharField(max_length=128)
  content = models.TextField(blank=True)
  creation_date = models.DateTimeField(auto_now_add=True)
  # It sets the time at which the entry was updated.
  last_updated_date = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Doc: {self.title} (in: {self.project_parent.title})"


class PendingEdit(models.Model):
  STATE_CHOICES = [
    ('pen', 'Pending'),
    ('acc', 'Accepted'),
    ('rej', 'Rejected'),
  ]

  collaborator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='proposed_edits'
  )
  document = models.ForeignKey(
    Document,
    on_delete=models.CASCADE,
    related_name='pending_edits'
  )
  modified_title = models.CharField(max_length=128)
  modified_content = models.TextField(blank=True)
  state = models.CharField(
    max_length=3,
    choices=STATE_CHOICES,
    default='pen' # By default, every proposed change is marked as pending.
  )
  creation_date = models.DateTimeField(auto_now_add=True)

  @staticmethod
  def can_user_propose_edit(user, document):
    """
    A user can only propose an edit to a document if it is a collaborator to the
    parent project.
    """
    project = document.project_parent
    # The owner does not need to suggest changes, but can edit the document directly.
    if project.is_owner(user):
      return False
    role = project.get_user_role(user)
    return role == "coll"

  def clean(self):
    super().clean()
    if self.document_id and self.collaborator_id:
      if self.document.project_parent.owner_id == self.collaborator_id:
        raise ValidationError(
          "The owner cannot create a PendingEdit; it can edit the document freely."
        )

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)

  def __str__(self):
    # get_state_display() converts the value of state to its associated label.
    return f"Edit of {self.collaborator.username} on '{self.document.title}' [{self.get_state_display()}]"