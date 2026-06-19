from django.urls import path
from . import views

app_name = 'documents' 

urlpatterns = [
  path('project/<int:project_id>/new/', views.DocumentCreateView.as_view(), name='create_document'),
  path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
  path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='edit_document'),
  path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='delete_document'),
]