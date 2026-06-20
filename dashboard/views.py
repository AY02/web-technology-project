from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404
from projects.models import Project
from projects.forms import ProjectCreateForm, ProjectEditForm, AddPermissionForm
from todos.models import ToDoEntry
from todos.forms import ToDoEntryForm


@login_required
def dashboard_view(request, project_id=None):
  user = request.user
  if project_id:
    project = get_object_or_404(Project, id=project_id)
  else:
    # Default view: root project
    project = Project.objects.filter(owner=user, parent__isnull=True).first()

  if not user.can_view(project):
    raise Http404('You do not have permission to view this project.')

  project_edit_form = None
  if user.can_edit_project(project):
    project_edit_form = ProjectEditForm(instance=project)

  project_create_form = None
  if user.is_owner_of(project):
    project_create_form = ProjectCreateForm()

  add_permission_form = None
  current_permissions = None
  if user.is_owner_of(project):
    add_permission_form = AddPermissionForm()
    current_permissions = project.user_permissions.all().select_related('user')

  todo_form = None
  if user.can_edit_todolist(project.todolist):
    todo_form = ToDoEntryForm()

  todo_entries = project.todolist.entries.all()

  calendar_entries = ToDoEntry.objects.filter(
    todo__project_parent_id__in=project.bfs(), deadline__isnull=False
  ).select_related('todo__project_parent').order_by('deadline')

  context = {
    'project': project,
    'can_view_parent': user.can_view_parent(project),
    'can_edit_document': user.can_edit_document_in(project),
    'can_comment': user.can_comment_on(project),
    'project_create_form': project_create_form,
    'project_edit_form': project_edit_form,
    'add_permission_form': add_permission_form,
    'current_permissions': current_permissions,
    'todo_form': todo_form,
    'todo_entries': todo_entries,
    'calendar_entries': calendar_entries,
  }

  return render(request, 'dashboard/dashboard.html', context)