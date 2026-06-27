from django.urls import path
from .views import (
  create_subproject,
  edit_project,
  delete_project,
  add_permission,
  remove_permission,
  search_public_projects,
  SharedProjectsListView,
  read_notification,
)


urlpatterns = [
  path('<int:parent_id>/create/', create_subproject, name='create_subproject'),
  path('<int:project_id>/edit/', edit_project, name='edit_project'),
  path('<int:project_id>/delete/', delete_project, name='delete_project'),
  path('<int:project_id>/add-permission/', add_permission, name='add_permission'),
  path('<int:project_id>/remove-permission/<int:permission_id>/', remove_permission, name='remove_permission'),
  path('shared_with_me/', SharedProjectsListView.as_view(), name='shared_projects'),
  
  # API Live Search
  path('search/public/', search_public_projects, name='search_public_projects'),
  path('notification/<int:notif_id>/read/', read_notification, name='read_notification'),
]