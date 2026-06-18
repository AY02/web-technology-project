from django.db import models


class ToDoList(models.Model):
  project_parent = models.OneToOneField(
    'projects.Project',
    on_delete=models.CASCADE,
    related_name='todolist'
  )

  def __str__(self):
    return f"To-Do List of {self.project_parent.title}"


class ToDoEntry(models.Model):
  todo = models.ForeignKey(
    ToDoList,
    on_delete=models.CASCADE,
    related_name='entries'
  )
  content = models.CharField(max_length=256)
  is_completed = models.BooleanField(default=False)
  # Entries with deadlines will be added to the dashboard calendar.
  deadline = models.DateTimeField(null=True, blank=True)
  last_updated_date = models.DateTimeField(auto_now=True)

  class Meta:
    # Default sorting:
    # 1. Show tasks to be done first, followed by those already completed.
    # 2. Show tasks that are about to expire first.
    ordering = ['is_completed', 'deadline']

  def __str__(self):
    state = "Done" if self.is_completed else "Not Done"
    return f"[{state}] {self.content[:32]}"