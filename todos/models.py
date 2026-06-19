from django.db import models
from django.utils import timezone
from django.db.models import F


class ToDoList(models.Model):
  project_parent = models.OneToOneField(
    'projects.Project',
    on_delete=models.CASCADE,
    related_name='todolist'
  )

  def __str__(self):
    return f'To-Do List of {self.project_parent.title}'


class ToDoEntry(models.Model):
  todo = models.ForeignKey(
    ToDoList,
    on_delete=models.CASCADE,
    related_name='entries'
  )
  content = models.CharField(max_length=256)
  is_completed = models.BooleanField(default=False)
  completion_date = models.DateTimeField(null=True, blank=True)
  deadline = models.DateTimeField(null=True, blank=True)
  last_updated_date = models.DateTimeField(auto_now=True)

  class Meta:
    # Default sorting:
    # 1. Show tasks to be done first, followed by those already completed.
    # 2. Show tasks that are about to expire first.
    ordering = ['is_completed', F('deadline').asc(nulls_last=True)]
    
    # Two todo entries cannot have the same content.
    constraints = [
      models.UniqueConstraint(
        fields=['todo', 'content'],
        name='unique_todo_content',
        violation_error_message='A task with this name already exists in this list.'
      )
    ]

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)

  def is_expired(self):
    '''Returns true if the deadline is expired.'''
    if self.deadline:
      return self.deadline.date() < timezone.now().date()
    return False

  def __str__(self):
    state = 'Done' if self.is_completed else 'Not Done'
    return f'[{state}] {self.content[:32]}'