from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import ValidationError
from .models import Project
from .forms import ProjectCreationForm, ProjectEditForm
from todos.models import ToDoList, ToDoEntry
from todos.forms import ToDoEntryForm


@login_required
def dashboard_view(request, project_id=None):
  if project_id:
    project = get_object_or_404(Project, id=project_id)
  else:
    # Default view: root project
    project = Project.objects.filter(owner=request.user, parent__isnull=True).first()

  if not project.can_view(request.user):
    raise Http404("You do not have permission to view this project.")

  project_edit_form = None
  if project.can_edit_project(request.user):
    project_edit_form = ProjectEditForm(instance=project)

  project_create_form = None
  if project.is_owner(request.user):
    project_create_form = ProjectCreationForm()

  todo_form = None
  if project.can_edit_todo_document(request.user):
    todo_form = ToDoEntryForm()

  calendar_entries = ToDoEntry.objects.filter(
    todo__project_parent_id__in=project.bfs(), deadline__isnull=False
  ).select_related('todo__project_parent').order_by('deadline')

  context = {
    'current_project': project,
    'is_owner': project.is_owner(request.user),
    'is_collaborator': project.is_coll(request.user),
    'can_view_parent': project.parent and project.parent.can_view(request.user),
    'creation_form': project_create_form,
    'edit_form': project_edit_form,
    'todo_entries': project.todolist.entries.all(),
    'todo_form': todo_form,
    'calendar_entries': calendar_entries,
  }

  return render(request, 'projects/dashboard.html', context)

@login_required
@require_POST
def create_subproject(request, parent_id):
  """
  After receiving data from the form we create the new subproject.
  """

  # The project to which the user wants to add a subproject needs to be of its
  # property.
  parent_project = get_object_or_404(Project, id=parent_id, owner=request.user)
  
  form = ProjectCreationForm(
    data=request.POST, user=request.user, parent_project=parent_project
  )
  if form.is_valid():
    form.save()
    messages.success(
      request, f"Subproject '{form.cleaned_data['title']}' created successfully."
    )
  else:
    messages.error(
      request, "Error creating subproject. Please check the provided data."
    )
  # Refreshing the page of the parent to see the new child.
  return redirect('dashboard_project', project_id=parent_project.id)

@login_required
@require_POST
def edit_project(request, project_id):
  """
  Update title and visibility of a subproject.
  """
  project = get_object_or_404(Project, id=project_id, owner=request.user)
  
  # Preventing root updates.
  if project.is_root():
    return redirect('dashboard')
    
  form = ProjectEditForm(request.POST, instance=project)
  if form.is_valid():
    form.save()
    messages.success(request, f"Project '{project.title}' updated successfully.")
  else:
    messages.error(
      request, "Error updating project. Please check the provided data."
    )
    
  return redirect('dashboard_project', project_id=project.id)

@login_required
@require_POST
def delete_project(request, project_id):
  """
  Delete a subproject and all of its children (CASCADE of the database).
  """
  project = get_object_or_404(Project, id=project_id, owner=request.user)
  
  # Preventing root updates.
  if project.is_root():
    return redirect('dashboard')
    
  parent_id = project.parent.id
  project_title = project.title
  project.delete()
  messages.success(
    request,
    f"Project '{project_title}' and all its contents were deleted successfully."
  )
  
  # Redirect to the parent after the delete.
  return redirect('dashboard_project', project_id=parent_id)


@login_required
@require_POST
def add_todo_entry(request, project_id):
  project = get_object_or_404(Project, id=project_id, owner=request.user)

  if not project.can_edit_todo_document(request.user):
    raise Http404("You do not have permission to add tasks.")

  todo_list = ToDoList.objects.get(project_parent=project)

  form = ToDoEntryForm(request.POST)
  if form.is_valid():
    new_entry = form.save(commit=False)
    new_entry.todo = todo_list
    try:
      new_entry.save()
      messages.success(request, "Task added successfully.")
    except ValidationError as e:
      # Model-related errors.
      messages.error(request, e.messages[0])
  else:
    # Form-related errors.
    messages.error(request, list(form.errors.values())[0][0])
        
  if project.is_root():
    return redirect('dashboard')
  
  return redirect('dashboard_project', project_id=project.id)

@login_required
def toggle_todo(request, entry_id):
  """
  Receive an AJAX request to invert the state 'is_completed' of a task.
  """
  entry = get_object_or_404(ToDoEntry, id=entry_id)
  project = entry.todo.project_parent
    
  # Permissions checks
  is_owner = project.owner == request.user
  is_collaborator = project.get_user_role(request.user) == 'coll'
    
  if is_owner or is_collaborator:
    entry.is_completed = not entry.is_completed

    if entry.is_completed:
      entry.completion_date = timezone.now()
    else:
      entry.completion_date = None

    entry.save()
    return HttpResponse("ok")
  return HttpResponse("error", status=403)


@login_required
@require_POST
def delete_todo_entry(request, entry_id):
  entry = get_object_or_404(ToDoEntry, id=entry_id)
  project = entry.todo.project_parent
    
  is_owner = project.owner == request.user
  is_collaborator = project.get_user_role(request.user) == 'coll'
    
  if not (is_owner or is_collaborator):
    raise Http404("You do not have permission to delete this task.")
        
  entry.delete()
  messages.success(request, "Task deleted successfully.")
    
  if project.parent is None:
    return redirect('dashboard')
  return redirect('dashboard_project', project_id=project.id)


@login_required
@require_POST
def edit_todo_entry(request, entry_id):
  entry = get_object_or_404(ToDoEntry, id=entry_id)
  project = entry.todo.project_parent
  
  is_owner = project.owner == request.user
  is_collaborator = project.get_user_role(request.user) == 'coll'
  if not (is_owner or is_collaborator):
    raise Http404("You do not have permission to edit this task.")
      
  form = ToDoEntryForm(request.POST, instance=entry, todo_list=entry.todo)
  if form.is_valid():
    form.save()
    messages.success(request, "Task updated successfully.")
  else:
    if form.non_field_errors():
      messages.error(request, form.non_field_errors()[0])
    else:
      messages.error(request, "Error updating task.")
          
  if project.parent is None:
    return redirect('dashboard')
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
    directory = p.parent.title if p.parent else f"Root ({p.owner.username})"
    
    results.append({
      'id': p.id,
      'title': p.title,
      'owner': p.owner.username,
      'directory': directory,
    })

  return JsonResponse({'results': results})