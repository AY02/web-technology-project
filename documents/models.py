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

  def is_owner(self, user):
    return self.project_parent.is_owner(user)

  def can_propose_edit(self, user):
    """
    A user can only propose an edit to a document if it is a collaborator to the
    parent project.
    """
    project = self.project_parent
    # The owner does not need to suggest changes, but can edit the document directly.
    if project.is_owner(user):
      return False
    role = project.get_user_role(user)
    return role == "coll"

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

  def accept(self):
    """
    Applies the proposed changes to the original document and updates the status.
    This should be called only by the project owner.
    """
    if self.state != "pen":
      return # Prevent re-accepting or accepting rejected edits

    doc = self.document
    doc.title = self.modified_title
    doc.content = self.modified_content
    doc.save()

    self.state = 'acc'
    self.save()

  def reject(self):
    """
    Marks the proposal as rejected. No changes are applied to the document.
    """
    if self.state == "pen":
      self.state = 'rej'
      self.save()

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
    collaborator = self.collaborator.username if self.collaborator else "User deleted"
    return f"Edit of {collaborator} on '{self.document.title}' [{self.get_state_display()}]"