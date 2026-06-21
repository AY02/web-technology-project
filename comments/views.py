from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from projects.models import Project
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