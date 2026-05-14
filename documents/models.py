from django.db import models
from django.conf import settings


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
    on_delete=models.CASCADE,
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

  def __str__(self):
    # get_state_display() converts the value of state to its associated label.
    return f"Edit of {self.collaborator.username} on '{self.document.title}' [{self.get_state_display()}]"