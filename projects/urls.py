from django.urls import path
from .views import dashboard_view, create_subproject

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    # if the url includes an additional parameter we include that project
    path('dashboard/<int:project_id>/', dashboard_view, name='dashboard_project'),
    path('dashboard/<int:parent_id>/create/', create_subproject, name='create_subproject'),
]