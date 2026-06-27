from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib import messages
from projects.models import Project, Notification
from .forms import CommentForm
from .models import Comment


@login_required
@require_POST
def add_comment(request, project_id):
  project = get_object_or_404(Project, id=project_id)

  if not request.user.can_comment_on(project):
    messages.error(request, 'You do not have permission to comment on this project.')
    return redirect('dashboard_project', project_id=project.id)
  
  form = CommentForm(request.POST)
  if form.is_valid():
    comment = form.save(commit=False)
    comment.project = project
    comment.user = request.user
    comment.save()

    # Identify all users who should be notified
    users_to_notify = set()
    users_to_notify.add(project.owner)
    for perm in project.get_permissions(allowed_roles=['comm','coll']):
      users_to_notify.add(perm.user)
    if request.user in users_to_notify:
      users_to_notify.remove(request.user)
    # web socket notification
    channel_layer = get_channel_layer()
    if users_to_notify:
      message_text = f"{request.user.username} added a comment in {project.title}"
      # save in the database
      for recipient in users_to_notify:
        notif = Notification.objects.create(
          recipient=recipient,
          message=message_text,
          project=project
        )

        read_url = reverse('read_notification', args=[notif.id])

        # async_to_sync because we are in a sinc view here
        async_to_sync(channel_layer.group_send)(
          f"notif_user_{recipient.id}",
          {
            'type': 'send_notification', 
            'message': message_text,
            'url': read_url # passing the url to js
          }
        )
  else:
    messages.error(request, 'Error posting comment. It cannot be empty.')

  return redirect('dashboard_project', project_id=project.id)


@login_required
@require_POST
def delete_comment(request, comment_id):
  comment = get_object_or_404(Comment, id=comment_id)
  project_id = comment.project.id

  if request.user.can_delete_comment(comment):
    comment.delete()
    messages.success(request, 'Comment deleted successfully.')
  else:
    messages.error(request, 'You do not have permission to delete this comment.')

  return redirect('dashboard_project', project_id=project_id)