from django.urls import path
from .views import add_todo_entry, toggle_todo_entry, delete_todo_entry, edit_todo_entry


urlpatterns = [
  path('list/<int:todolist_id>/add/', add_todo_entry, name='add_todo_entry'),
  path('edit/<int:entry_id>/', edit_todo_entry, name='edit_todo_entry'),
  path('delete/<int:entry_id>/', delete_todo_entry, name='delete_todo_entry'),
  path('toggle/<int:entry_id>/', toggle_todo_entry, name='toggle_todo_entry'),
]