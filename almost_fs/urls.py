from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
  path('admin/', admin.site.urls),
  
  # Homepage
  path('', TemplateView.as_view(template_name='index.html'), name='home'),
  
  # App routes
  path('accounts/', include('accounts.urls')),
  path('dashboard/', include('dashboard.urls')),
  path('projects/', include('projects.urls')),
  path('todos/', include('todos.urls')),
  path('documents/', include('documents.urls')),
  path('comments/', include('comments.urls')),
]