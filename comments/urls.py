from django.urls import path
from . import views


app_name = 'comments'


urlpatterns = [
  path('project/<int:project_id>/add/', views.add_comment, name='add_comment'),
  path('project/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]