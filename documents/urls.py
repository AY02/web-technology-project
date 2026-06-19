from django.urls import path
from . import views

app_name = 'documents' 

urlpatterns = [
  path('project/<int:project_id>/new/', views.DocumentCreateView.as_view(), name='create_document'),
]