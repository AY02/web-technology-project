from django.contrib import admin
from .models import Project, ProjectPermission


admin.site.register(Project)
admin.site.register(ProjectPermission)