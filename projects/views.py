from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.exceptions import ValidationError
from .models import Project
from .forms import ProjectCreateForm, ProjectEditForm


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
def edit_project(request, parent_id):
  project = get_object_or_404(Project, id=parent_id)

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