from django.urls import path
from .views import dashboard_view


urlpatterns = [
  # Base Route (Root Project)
  path('', dashboard_view, name='dashboard'),  
  # Project-specific Route
  path('<int:project_id>/', dashboard_view, name='dashboard_project'),
]