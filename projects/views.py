from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from .models import Project
from .forms import ProjectCreationForm, ProjectEditForm
from todos.models import ToDoList, ToDoEntry
from todos.forms import ToDoEntryForm

@login_required
def dashboard_view(request, project_id=None):
  if project_id:
    current_project = get_object_or_404(Project, id=project_id)
    is_owner = (current_project.owner == request.user)
    is_public = (current_project.visibility == 'pub')
    has_role = current_project.get_user_role(request.user) is not None
    if not (is_owner or is_public or has_role):
      raise Http404("You do not have permission to view this project.")
  else:
    current_project = Project.objects.filter(
      owner=request.user, parent__isnull=True
    ).first()
  
  subprojects = current_project.subprojects.all() if current_project else []
  parent_project = current_project.parent if current_project else None
  
  # We create the edit form only if we are not in the root and we are the owner.
  edit_form = None
  if (
    current_project and
    current_project.parent is not None and
    current_project.owner == request.user
  ):
    edit_form = ProjectEditForm(instance=current_project)

  # todo logics
  todo_entries = []
  if current_project:
    if hasattr(current_project, 'todolist'):
      todo_entries = current_project.todolist.entries.all()

  # We only pass the form for the todos if you are an owner or collaborator.
  todo_form = None
  if current_project:
    is_owner = (current_project.owner == request.user)
    is_collaborator = (current_project.get_user_role(request.user) == 'coll')
    if is_owner or is_collaborator:
      todo_form = ToDoEntryForm()

  context = {
    'current_project': current_project,
    'subprojects': subprojects,
    'parent_project': parent_project,
    'creation_form': ProjectCreationForm(),
    'edit_form': edit_form,
    'todo_entries': todo_entries,
    'todo_form': todo_form,
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
  if project.parent is None:
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
  if project.parent is None:
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
  
  # Permissions check
  is_owner = project.owner == request.user
  is_collaborator = project.get_user_role(request.user) == 'coll'
  if not (is_owner or is_collaborator):
    raise Http404("You do not have permission to add tasks.")

  # To be removed the "or_create" logic probably: defensive approach, 
  # if we have data from before the trigger implementation, we create the todo 
  todo_list, created = ToDoList.objects.get_or_create(project_parent=project)
    
  form = ToDoEntryForm(request.POST, todo_list=todo_list)
  if form.is_valid():
    new_entry = form.save(commit=False)
    new_entry.todo = todo_list
    new_entry.save()
    messages.success(request, "Task added successfully.")
  else:
    error_msg = form.non_field_errors()[0] or "Error adding task."
    messages.error(request, error_msg)
        
  if project.parent is None:
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