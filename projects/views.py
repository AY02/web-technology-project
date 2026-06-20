from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Project, ProjectPermission
from .forms import ProjectCreateForm, ProjectEditForm, AddPermissionForm


@login_required
@require_POST
def create_subproject(request, parent_id):
  # The project to which the user wants to add a subproject needs to be of its
  # property.
  parent_project = get_object_or_404(Project, id=parent_id)

  if not request.user.is_owner_of(parent_project):
    raise Http404('You do not have permission to create subprojects here.')

  form = ProjectCreateForm(
    data=request.POST,
    user=request.user,
    parent_project=parent_project
  )
  if form.is_valid():
    try:
      form.save()
      messages.success(
        request,
        f"Subproject '{form.cleaned_data['title']}' created successfully."
      )
    except ValidationError as e:
      # Model-related errors.
      messages.error(request, e.messages[0])
  else:
    # Form-related errors.
    messages.error(request, list(form.errors.values())[0][0])

  # Redirecting the page of the parent to see the new child.
  return redirect('dashboard_project', project_id=parent_project.id)


@login_required
@require_POST
def edit_project(request, project_id):
  project = get_object_or_404(Project, id=project_id)

  if not request.user.can_edit_project(project):
    raise Http404('You do not have permission to edit this project.')

  form = ProjectEditForm(request.POST, instance=project)
  if form.is_valid():
    try:
      form.save()
      messages.success(request, f"Project '{project.title}' updated successfully.")
    except ValidationError as e:
      # Model-related errors.
      messages.error(request, e.messages[0])
  else:
    # Form-related errors.
    messages.error(request, list(form.errors.values())[0][0])

  return redirect('dashboard_project', project_id=project.id)


@login_required
@require_POST
def delete_project(request, project_id):
  project = get_object_or_404(Project, id=project_id)

  if not request.user.can_edit_project(project):
    raise Http404('You do not have permission to delete this project.')

  parent_id = project.parent.id
  project_title = project.title
  try:
    project.delete()
    messages.success(
      request,
      f"Project '{project_title}' and all its contents were deleted successfully."
    )
  except ValidationError as e:
    # Model-related errors.
    messages.error(request, e.messages[0])

  # Redirect to the parent after the delete.
  return redirect('dashboard_project', project_id=parent_id)


@login_required
@require_POST
def add_permission(request, project_id):
  project = get_object_or_404(Project, id=project_id)
    
  if not request.user.is_owner_of(project):
    messages.error(request, "Only the project owner can manage access.")
    return redirect('dashboard_project', project_id=project.id)

  form = AddPermissionForm(request.POST)
  if form.is_valid():
    username = form.cleaned_data['username']
    role = form.cleaned_data['role']
    readable_role = dict(form.fields['role'].choices).get(role, role)
    User = get_user_model()

    # Check of user's existence
    try:
      target_user = User.objects.get(username=username)
    except User.DoesNotExist:
      messages.error(request, f"User '{username}' not found. Check the spelling.")
      return redirect('dashboard_project', project_id=project.id)

    # Owner cannot invite himself
    if target_user == request.user:
      messages.warning(request, "You cannot assign roles to yourself.")
      return redirect('dashboard_project', project_id=project.id)

    # Creating or updating the permission
    ProjectPermission.objects.update_or_create(
      user=target_user,
      project=project,
      defaults={'role': role}
    )
        
    messages.success(request, f"Successfully assigned role of {readable_role} to '{username}'.")
  else:
    messages.error(request, "Invalid form submission.")

  return redirect('dashboard_project', project_id=project.id)


@login_required
@require_POST
def remove_permission(request, project_id, permission_id):
  project = get_object_or_404(Project, id=project_id)
  
  if not request.user.is_owner_of(project):
    messages.error(request, "Only the project owner can manage access.")
    return redirect('dashboard_project', project_id=project.id)

  # The permission must belong to this project
  permission = get_object_or_404(ProjectPermission, id=permission_id, project=project)
  username = permission.user.username
  
  permission.delete()
  messages.success(request, f"Access revoked for '{username}'.")
  return redirect('dashboard_project', project_id=project.id)


@login_required
def search_public_projects(request):
  """
  Returns a JSON containing public projects matching the query.
  Called via AJAX on every keystroke for the live search.
  """
  query = request.GET.get('query', '').strip()
  
  if not query:
    return JsonResponse({'results': []})

  # Filter public projects containing the query string (case-insensitive).
  # select_related optimizes database queries by fetching owner and parent
  # immediately.
  projects = Project.objects.filter(
    visibility='pub', 
    title__icontains=query
  ).select_related('owner', 'parent')[:10]

  results = []
  for p in projects:
    # Disambiguation: if it has no parent, it resides in the user's Root project.
    directory = p.parent.title if p.parent else f'Root ({p.owner.username})'
    
    results.append({
      'id': p.id,
      'title': p.title,
      'owner': p.owner.username,
      'directory': directory,
    })

  return JsonResponse({'results': results})


class SharedProjectsListView(LoginRequiredMixin, ListView):
  model = ProjectPermission 
  template_name = 'projects/shared_projects.html'
  context_object_name = 'shared_permissions'

  def get_queryset(self):
    return ProjectPermission.objects.filter(
      user=self.request.user
    ).select_related('project', 'project__owner').order_by('-project__creation_date')