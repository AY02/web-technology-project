from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Project
from .forms import ProjectCreationForm, ProjectEditForm
from todos.models import ToDoList, ToDoEntry
from todos.forms import ToDoEntryForm

@login_required
def dashboard_view(request, project_id=None):
  if project_id:
    current_project = get_object_or_404(Project, id=project_id, owner=request.user)
  else:
    current_project = Project.objects.filter(
      owner=request.user, parent__isnull=True
    ).first()
  
  subprojects = current_project.subprojects.all() if current_project else []
  parent_project = current_project.parent if current_project else None
  
  # We create the edit form only if we are not in the root.
  edit_form = None
  if current_project and current_project.parent is not None:
    edit_form = ProjectEditForm(instance=current_project)

  # todo logics
  todo_entries = []
  if current_project:
    if hasattr(current_project, 'todolist'):
      todo_entries = current_project.todolist.entries.all()

  context = {
    'current_project': current_project,
    'subprojects': subprojects,
    'parent_project': parent_project,
    'creation_form': ProjectCreationForm(),
    'edit_form': edit_form,
    'todo_entries': todo_entries,
    'todo_form': ToDoEntryForm(),
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
    
  # To be removed the "or_create" logic probably: defensive approach, 
  # if we have data from before the trigger implementation, we create the todo 
  todo_list, created = ToDoList.objects.get_or_create(project_parent=project)
    
  form = ToDoEntryForm(request.POST)
  if form.is_valid():
    new_entry = form.save(commit=False)
    new_entry.todo = todo_list
    new_entry.save()
    messages.success(request, "Task added successfully.")
  else:
    messages.error(request, "Error adding task.")
        
  if project.parent is None:
    return redirect('dashboard')
  return redirect('dashboard_project', project_id=project.id)