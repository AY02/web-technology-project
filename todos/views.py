from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from .models import ToDoList, ToDoEntry
from .forms import ToDoEntryForm


@login_required
@require_POST
def add_todo_entry(request, todolist_id):
  todo_list = get_object_or_404(ToDoList, id=todolist_id)

  if not request.user.can_edit_todolist(todo_list):
    raise Http404('You do not have permission to add tasks.')

  form = ToDoEntryForm(request.POST)
  if form.is_valid():
    new_entry = form.save(commit=False)
    new_entry.todo = todo_list
    try:
      new_entry.save()
      messages.success(request, 'Task added successfully.')
    except ValidationError as e:
      # Model-related errors.
      messages.error(request, e.messages[0])
  else:
    # Form-related errors.
    messages.error(request, list(form.errors.values())[0][0])

  project = todo_list.project_parent
  if project.is_root():
    return redirect('dashboard')
  
  return redirect('dashboard_project', project_id=project.id)


@login_required
@require_POST
def edit_todo_entry(request, entry_id):
  entry = get_object_or_404(ToDoEntry, id=entry_id)
  project = entry.todo.project_parent
  
  if not request.user.can_edit_todolist(entry.todo):
    raise Http404('You do not have permission to edit this task.')

  form = ToDoEntryForm(request.POST, instance=entry, todo_list=entry.todo)
  if form.is_valid():
    try:
      form.save()
      messages.success(request, 'Task updated successfully.')
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
@require_POST
def delete_todo_entry(request, entry_id):
  entry = get_object_or_404(ToDoEntry, id=entry_id)
  project = entry.todo.project_parent
    
  if not request.user.can_edit_todolist(entry.todo):
    raise Http404('You do not have permission to delete this task.')

  entry.delete()
  messages.success(request, 'Task deleted successfully.')
    
  if project.is_root():
    return redirect('dashboard')
  return redirect('dashboard_project', project_id=project.id)


@login_required
def toggle_todo_entry(request, entry_id):
  """Receive an AJAX request to invert the state 'is_completed' of a task."""
  entry = get_object_or_404(ToDoEntry, id=entry_id)
  if request.user.can_edit_todolist(entry.todo):
    entry.is_completed = not entry.is_completed
    entry.completion_date = timezone.now() if entry.is_completed else None
    entry.save()
    return HttpResponse('ok')   
  return HttpResponse('error', status=403)