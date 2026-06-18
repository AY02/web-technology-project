from django.urls import path
from .views import (
  dashboard_view,
  create_subproject,
  edit_project,
  delete_project,
  add_todo_entry,
  search_public_projects
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
  # API Live Search
  path(
    'dashboard/search/public/', search_public_projects, name='search_public_projects'
  )
]