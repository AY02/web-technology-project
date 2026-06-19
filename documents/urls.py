from django.urls import path
from . import views

app_name = 'documents' 

urlpatterns = [
  path('project/<int:project_id>/new/', views.DocumentCreateView.as_view(), name='create_document'),
  path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
  path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='edit_document'),
  path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='delete_document'),
  path('<int:document_id>/propose/', views.ProposeEditView.as_view(), name='propose_edit'),
  path('project/<int:project_id>/review/', views.ReviewEditsView.as_view(), name='review_edits'),  
  path('edit/<int:edit_id>/<str:action>/', views.handle_pending_edit, name='handle_edit'),
]