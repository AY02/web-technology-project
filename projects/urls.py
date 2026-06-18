from django.urls import path
from .views import (
  dashboard_view,
  create_subproject,
  edit_project,
  delete_project,
  add_todo_entry,
  toggle_todo,
  delete_todo_entry,
  edit_todo_entry,
  search_public_projects,
)

urlpatterns = [
  path('dashboard/', dashboard_view, name='dashboard'),
  # If the url includes an additional parameter we include that project.
  path('dashboard/<int:project_id>/', dashboard_view, name='dashboard_project'),
  path(
    'dashboard/<int:parent_id>/create/',
    create_subproject,
    name='create_subproject'
  ),
  path('dashboard/<int:project_id>/edit/', edit_project, name='edit_project'),
  path('dashboard/<int:project_id>/delete/', delete_project, name='delete_project'),
  path('dashboard/<int:project_id>/add-todo/', add_todo_entry, name='add_todo_entry'),
  path('dashboard/todo/toggle/<int:entry_id>/', toggle_todo, name='toggle_todo'),
  path('dashboard/todo/delete/<int:entry_id>/', delete_todo_entry, name='delete_todo_entry'),
  path('dashboard/todo/edit/<int:entry_id>/', edit_todo_entry, name='edit_todo_entry'),
  # API Live Search
  path(
    'dashboard/search/public/', search_public_projects, name='search_public_projects'
  ),
]