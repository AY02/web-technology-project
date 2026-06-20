from django.db import models
from django.conf import settings


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

  content = models.TextField()
  creation_date = models.DateTimeField(auto_now_add=True)

  class Meta:
    # By default, we sort from newest to oldest.
    ordering = ['-creation_date']

  def __str__(self):
    author = self.user.username if self.user else 'User deleted'
    return f'Comment of {author} on {self.project.title}'